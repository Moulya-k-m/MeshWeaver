"""Day 17 remote task status query tests."""

import asyncio
import unittest

from unittest.mock import Mock, patch

from meshweaver.broker import (
    Worker,
    decode,
    start_client,
)


async def slow_square(number):
    await asyncio.sleep(0.8)
    return number * number


async def failing_task(number):
    await asyncio.sleep(0.1)
    raise ValueError("Intentional failure")


class StatusQueryTests(unittest.IsolatedAsyncioTestCase):

    async def asyncSetUp(self):
        loop = asyncio.get_running_loop()

        self.worker_transport, self.worker = (
            await loop.create_datagram_endpoint(
                lambda: Worker(
                    max_concurrent=1,
                    max_queue=5,
                ),
                local_addr=("127.0.0.1", 0),
            )
        )

        self.port = (
            self.worker_transport
            .get_extra_info("sockname")[1]
        )

        self.client_transport, self.client = (
            await start_client(port=self.port)
        )

        self.submissions = []

    async def asyncTearDown(self):
        await self.worker.shutdown(
            cancel_pending=True
        )

        await asyncio.gather(
            *self.submissions,
            return_exceptions=True,
        )

        self.client_transport.close()
        self.worker_transport.close()

        await asyncio.sleep(0)

    async def wait_until(self, condition):
        for _ in range(200):
            if condition():
                return

            await asyncio.sleep(0.005)

        self.fail("Condition not reached")

    async def submit_task(self, function=slow_square):
        previous = set(self.client.pending)

        submission = asyncio.create_task(
            self.client.submit(
                function,
                5,
                timeout=5.0,
                retries=0,
            )
        )

        self.submissions.append(submission)

        await self.wait_until(
            lambda: bool(
                set(self.client.pending) - previous
            )
        )

        task_id = next(
            iter(set(self.client.pending) - previous)
        )

        await self.wait_until(
            lambda: self.worker.get_task_status(
                task_id
            ) is not None
        )

        return task_id, submission

    async def test_queued_status(self):
        first_id, first = await self.submit_task()

        await self.wait_until(
            lambda: self.worker.get_task_status(
                first_id
            )["state"] == "RUNNING"
        )

        task_id, submission = await self.submit_task()

        status = await self.client.query_task_status(
            task_id
        )

        self.assertEqual(status["state"], "QUEUED")
        self.assertIsNone(status["started_at"])

        self.assertEqual(await first, 25)
        self.assertEqual(await submission, 25)

    async def test_running_status(self):
        task_id, submission = await self.submit_task()

        await self.wait_until(
            lambda: self.worker.get_task_status(
                task_id
            )["state"] == "RUNNING"
        )

        status = await self.client.query_task_status(
            task_id
        )

        self.assertEqual(status["state"], "RUNNING")
        self.assertIsNotNone(status["started_at"])
        self.assertIsNone(status["completed_at"])

        self.assertEqual(await submission, 25)

    async def test_completed_status(self):
        task_id, submission = await self.submit_task()

        self.assertEqual(await submission, 25)

        before = self.client.get_metrics()

        status = await self.client.query_task_status(
            task_id
        )

        self.assertEqual(status["state"], "COMPLETED")
        self.assertIsNotNone(status["completed_at"])

        self.assertEqual(
            self.client.get_metrics(),
            before,
        )

    async def test_failed_status(self):
        task_id, submission = await self.submit_task(
            failing_task
        )

        with self.assertRaises(RuntimeError):
            await submission

        status = await self.client.query_task_status(
            task_id
        )

        self.assertEqual(status["state"], "FAILED")
        self.assertIn("ValueError", status["error"])

    async def test_cancelled_status(self):
        task_id, submission = await self.submit_task()

        self.assertTrue(
            await self.client.cancel_task(task_id)
        )

        with self.assertRaisesRegex(
            RuntimeError, "Task cancelled"
        ):
            await submission

        status = await self.client.query_task_status(
            task_id
        )

        self.assertEqual(status["state"], "CANCELLED")
        self.assertIsNotNone(status["completed_at"])

    async def test_unknown_task_status(self):
        status = await self.client.query_task_status(
            "unknown-task"
        )

        self.assertIsNone(status)
        self.assertEqual(self.client.status_pending, {})

    async def test_unauthorized_status_query(self):
        task_id, submission = await self.submit_task()

        other_transport, other_client = (
            await start_client(port=self.port)
        )

        try:
            status = await other_client.query_task_status(
                task_id
            )

            self.assertIsNone(status)

            owner_status = (
                await self.client.query_task_status(
                    task_id
                )
            )

            self.assertIsNotNone(owner_status)

            self.assertEqual(await submission, 25)

            self.assertIsNone(
                await other_client.query_task_status(
                    task_id
                )
            )

        finally:
            other_transport.close()

    async def test_invalid_query_parameters(self):
        for invalid_id in ("", None, 123, "x" * 65):
            with self.subTest(task_id=invalid_id):
                with self.assertRaises(ValueError):
                    await self.client.query_task_status(
                        invalid_id
                    )

        with self.assertRaises(ValueError):
            await self.client.query_task_status(
                "task-1",
                timeout=0,
            )

        with self.assertRaises(ValueError):
            await self.client.query_task_status(
                "task-1",
                retries=-1,
            )

        self.assertEqual(self.client.status_pending, {})

    async def test_status_timeout_and_cleanup(self):
        original = self.client.transport
        proxy = Mock(wraps=original)
        proxy.sendto.return_value = None
        proxy.sendto.side_effect = lambda *args: None

        with patch.object(
            self.client, "transport", proxy
        ):
            with self.assertRaises(TimeoutError):
                await self.client.query_task_status(
                    "missing-task",
                    timeout=0.05,
                    retries=1,
                )

        self.assertEqual(proxy.sendto.call_count, 2)
        self.assertEqual(self.client.status_pending, {})

    async def test_status_response_packet_loss(self):
        task_id, submission = await self.submit_task()

        self.assertEqual(await submission, 25)

        original = self.worker.transport
        proxy = Mock(wraps=original)

        dropped = []

        def sendto(packet, addr):
            message = decode(packet)

            if (
                message.get("type") == "status_response"
                and not dropped
            ):
                dropped.append(True)
                return

            original.sendto(packet, addr)

        proxy.sendto.side_effect = sendto

        with patch.object(
            self.worker, "transport", proxy
        ):
            status = await self.client.query_task_status(
                task_id,
                timeout=0.1,
                retries=2,
            )

        self.assertEqual(len(dropped), 1)
        self.assertEqual(proxy.sendto.call_count, 2)
        self.assertEqual(status["state"], "COMPLETED")
        self.assertEqual(self.client.status_pending, {})


if __name__ == "__main__":
    unittest.main()
