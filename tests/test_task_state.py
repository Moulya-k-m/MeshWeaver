"""Day 16 lifecycle and cancellation metrics tests."""

import asyncio
import unittest

from unittest.mock import Mock, patch

from meshweaver.task_state import TaskRegistry, TaskState
from meshweaver.metrics import TaskMetrics
from meshweaver.broker import (
    Worker, Client, decode, start_client
)


async def slow_task(number):
    await asyncio.sleep(0.5)
    return number * number


async def failing_task(number):
    await asyncio.sleep(0.1)
    raise ValueError("Intentional failure")


class TaskStateTests(unittest.TestCase):

    def test_initial_task_state(self):
        registry = TaskRegistry()
        registry.create("task-1")

        record = registry.get("task-1")

        self.assertEqual(record["state"], "SUBMITTED")
        self.assertIsNotNone(record["submitted_at"])
        self.assertIsNone(record["completed_at"])

    def test_invalid_state_transition(self):
        registry = TaskRegistry()
        registry.create("task-1")

        self.assertFalse(
            registry.transition(
                "task-1", TaskState.COMPLETED
            )
        )

        self.assertEqual(
            registry.get("task-1")["state"],
            "SUBMITTED"
        )

    def test_unknown_task_status(self):
        registry = TaskRegistry()

        self.assertIsNone(registry.get("missing"))

        self.assertFalse(
            registry.transition(
                "missing", TaskState.RUNNING
            )
        )

    def test_cancellation_metrics(self):
        metrics = TaskMetrics()

        for _ in range(3):
            metrics.record_submission()

        metrics.record_success(0.2)
        metrics.record_failure(0.3)
        metrics.record_cancellation(0.1)

        result = metrics.snapshot()

        self.assertEqual(result["successful"], 1)
        self.assertEqual(result["failed"], 1)
        self.assertEqual(result["cancelled"], 1)
        self.assertEqual(result["pending"], 0)
        self.assertEqual(
            result["cancellation_rate"], 33.33
        )


class LifecycleIntegrationTests(
    unittest.IsolatedAsyncioTestCase
):

    async def asyncSetUp(self):
        loop = asyncio.get_running_loop()

        self.worker_transport, self.worker = (
            await loop.create_datagram_endpoint(
                lambda: Worker(
                    max_concurrent=1,
                    max_queue=5
                ),
                local_addr=("127.0.0.1", 0)
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
            return_exceptions=True
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

    async def submit_task(self, function=slow_task):
        previous = set(self.client.pending)

        submission = asyncio.create_task(
            self.client.submit(
                function, 5,
                timeout=3.0,
                retries=0
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

    async def test_queued_task_state(self):
        first_id, first = await self.submit_task()
        task_id, submission = await self.submit_task()

        self.assertEqual(
            self.worker.get_task_status(
                task_id
            )["state"],
            "QUEUED"
        )

        self.assertEqual(await first, 25)
        self.assertEqual(await submission, 25)

    async def test_running_task_state(self):
        task_id, submission = await self.submit_task()

        await self.wait_until(
            lambda: self.worker.get_task_status(
                task_id
            )["state"] == "RUNNING"
        )

        record = self.worker.get_task_status(task_id)

        self.assertIsNotNone(record["started_at"])
        self.assertIsNone(record["completed_at"])

        self.assertEqual(await submission, 25)

    async def test_completed_task_state(self):
        task_id, submission = await self.submit_task()

        self.assertEqual(await submission, 25)

        record = self.worker.get_task_status(task_id)

        self.assertEqual(record["state"], "COMPLETED")
        self.assertIsNotNone(record["completed_at"])

    async def test_failed_task_state(self):
        task_id, submission = await self.submit_task(
            failing_task
        )

        with self.assertRaises(RuntimeError):
            await submission

        record = self.worker.get_task_status(task_id)

        self.assertEqual(record["state"], "FAILED")
        self.assertIn("ValueError", record["error"])

    async def test_cancelled_task_state_and_metrics(self):
        task_id, submission = await self.submit_task()

        self.assertTrue(
            await self.client.cancel_task(task_id)
        )

        with self.assertRaisesRegex(
            RuntimeError, "Task cancelled"
        ):
            await submission

        record = self.worker.get_task_status(task_id)
        metrics = self.client.get_metrics()

        self.assertEqual(record["state"], "CANCELLED")
        self.assertIsNotNone(record["completed_at"])

        self.assertEqual(metrics["cancelled"], 1)
        self.assertEqual(metrics["failed"], 0)
        self.assertEqual(metrics["pending"], 0)
        self.assertEqual(
            metrics["cancellation_accepted"], 1
        )

    async def test_unauthorized_cancellation_and_ack_loss(self):
        task_id, submission = await self.submit_task()

        other_transport, other_client = (
            await start_client(port=self.port)
        )

        try:
            self.assertFalse(
                await other_client.cancel_task(task_id)
            )

            self.assertEqual(
                other_client.get_metrics()[
                    "cancellation_rejected"
                ],
                1
            )

            original = self.worker.transport
            proxy = Mock(wraps=original)
            dropped = []

            def sendto(packet, addr):
                message = decode(packet)

                if (
                    message.get("type") == "cancel_ack"
                    and not dropped
                ):
                    dropped.append(True)
                    return

                original.sendto(packet, addr)

            proxy.sendto.side_effect = sendto

            with patch.object(
                self.worker, "transport", proxy
            ):
                self.assertTrue(
                    await self.client.cancel_task(
                        task_id,
                        timeout=0.1,
                        retries=2
                    )
                )

            with self.assertRaisesRegex(
                RuntimeError, "Task cancelled"
            ):
                await submission

            metrics = self.client.get_metrics()

            self.assertEqual(len(dropped), 1)
            self.assertEqual(
                metrics["cancellation_retries"], 1
            )
            self.assertEqual(
                metrics["cancellation_timeouts"], 1
            )
            self.assertEqual(
                self.worker.cancelled_count, 1
            )
            self.assertEqual(metrics["cancelled"], 1)

        finally:
            other_transport.close()


if __name__ == "__main__":
    unittest.main()
