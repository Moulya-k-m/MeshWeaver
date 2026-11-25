"""Tests for remote task cancellation over UDP."""

import asyncio
import time
import unittest

from unittest.mock import Mock

from meshweaver.broker import (
    Worker,
    Client,
    encode,
    start_client,
)


async def slow_square(number):
    await asyncio.sleep(0.5)
    return number * number


def sync_square(number):
    time.sleep(0.3)
    return number * number


class RemoteCancellationTests(
    unittest.IsolatedAsyncioTestCase
):

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

        port = self.worker_transport.get_extra_info(
            "sockname"
        )[1]

        self.client_transport, self.client = (
            await start_client(port=port)
        )

        self.submissions = []

    async def asyncTearDown(self):
        await self.worker.shutdown(cancel_pending=True)

        if self.submissions:
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

        self.fail("Condition was not reached")

    async def submit_task(self, function=slow_square):
        previous = set(self.client.pending)

        submission = asyncio.create_task(
            self.client.submit(
                function,
                5,
                timeout=2.0,
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
            lambda: task_id in self.worker.task_map
        )

        return task_id, submission

    async def test_remote_queued_cancellation(self):
        first_id, first = await self.submit_task()

        task_id, submission = await self.submit_task()

        await self.wait_until(
            lambda: task_id in self.worker.waiting
        )

        self.assertTrue(
            await self.client.cancel_task(task_id)
        )

        with self.assertRaisesRegex(
            RuntimeError, "Task cancelled"
        ):
            await submission

        self.assertNotIn(task_id, self.worker.waiting)

        self.assertEqual(await first, 25)

    async def test_remote_running_cancellation(self):
        task_id, submission = await self.submit_task()

        await self.wait_until(
            lambda: self.worker.running == 1
        )

        self.assertTrue(
            await self.client.cancel_task(task_id)
        )

        with self.assertRaisesRegex(
            RuntimeError, "Task cancelled"
        ):
            await submission

        self.assertEqual(self.worker.running, 0)

    async def test_unknown_task_cancellation(self):
        self.assertFalse(
            await self.client.cancel_task("unknown")
        )

    async def test_completed_task_cancellation(self):
        task_id, submission = await self.submit_task()

        self.assertEqual(await submission, 25)

        self.assertFalse(
            await self.client.cancel_task(task_id)
        )

    async def test_duplicate_cancellation(self):
        task_id, submission = await self.submit_task()

        results = await asyncio.gather(
            self.client.cancel_task(task_id),
            self.client.cancel_task(task_id),
        )

        self.assertEqual(results, [True, True])

        self.assertEqual(
            self.worker.cancelled_count, 1
        )

        self.assertTrue(
            await self.client.cancel_task(task_id)
        )

        self.assertEqual(
            self.worker.cancelled_count, 1
        )

        with self.assertRaises(RuntimeError):
            await submission

    async def test_invalid_cancellation_message(self):
        transport = Mock()
        worker = Worker()
        worker.connection_made(transport)

        worker.datagram_received(
            encode({
                "type": "cancel",
                "id": [],
                "request_id": "request-1",
            }),
            ("127.0.0.1", 12345),
        )

        transport.sendto.assert_not_called()

        self.assertEqual(
            len(worker.cancel_handlers), 0
        )

        with self.assertRaises(ValueError):
            await self.client.cancel_task("")

    async def test_cancellation_timeout(self):
        client = Client()
        transport = Mock()
        client.connection_made(transport)

        with self.assertRaises(TimeoutError):
            await client.cancel_task(
                "missing",
                timeout=0.01,
                retries=1,
            )

        self.assertEqual(
            transport.sendto.call_count, 2
        )

        self.assertEqual(
            len(client.cancel_pending), 0
        )

    async def test_cancellation_tracking_cleanup(self):
        task_id, submission = await self.submit_task()

        self.assertIn(
            task_id,
            self.client.get_active_task_ids(),
        )

        await self.client.cancel_task(task_id)

        with self.assertRaises(RuntimeError):
            await submission

        self.assertEqual(
            len(self.client.cancel_pending), 0
        )

        self.assertNotIn(
            task_id, self.client.pending
        )

        self.assertNotIn(
            task_id, self.worker.in_flight
        )

    async def test_sync_cancellation_rejected(self):
        task_id, submission = await self.submit_task(
            sync_square
        )

        await self.wait_until(
            lambda: task_id in self.worker.sync_running
        )

        self.assertFalse(
            await self.client.cancel_task(task_id)
        )

        self.assertEqual(await submission, 25)

    async def test_cancellation_result_delivery(self):
        task_id, submission = await self.submit_task()

        self.assertTrue(
            await self.client.cancel_task(task_id)
        )

        with self.assertRaisesRegex(
            RuntimeError, "Task cancelled"
        ):
            await submission

        self.assertIn(
            task_id, self.worker.completed
        )

        self.assertEqual(
            self.worker.cancelled_count, 1
        )


if __name__ == "__main__":
    unittest.main()
