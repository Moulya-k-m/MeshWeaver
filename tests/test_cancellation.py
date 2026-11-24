"""Tests for task cancellation and graceful shutdown."""

import asyncio
import unittest
from unittest.mock import Mock

from meshweaver.broker import Worker, decode
from tests.test_deduplication import create_packet, ADDRESS


async def slow_task(number):
    await asyncio.sleep(0.2)
    return number * number


class CancellationTests(unittest.IsolatedAsyncioTestCase):

    async def asyncSetUp(self):
        self.worker = Worker(
            max_concurrent=1,
            max_queue=5,
        )

        self.transport = Mock()
        self.worker.connection_made(self.transport)

    async def asyncTearDown(self):
        if self.worker.tasks:
            await asyncio.gather(
                *list(self.worker.tasks),
                return_exceptions=True,
            )

    def send_task(self, task_id):
        packet = create_packet(
            task_id, slow_task, 5
        )

        self.worker.datagram_received(
            packet, ADDRESS
        )

        return packet

    async def test_cancel_queued_task(self):
        self.send_task("running")
        self.send_task("queued")

        await asyncio.sleep(0)

        cancelled = await self.worker.cancel_task("queued")

        self.assertTrue(cancelled)
        self.assertNotIn("queued", self.worker.waiting)
        self.assertNotIn("queued", self.worker.in_flight)

        result = decode(self.worker.completed["queued"])

        self.assertFalse(result["ok"])
        self.assertEqual(result["error"], "Task cancelled")

    async def test_cancel_running_task(self):
        self.send_task("running-task")

        await asyncio.sleep(0)

        self.assertEqual(self.worker.running, 1)

        cancelled = await self.worker.cancel_task(
            "running-task"
        )

        self.assertTrue(cancelled)
        self.assertEqual(self.worker.running, 0)
        self.assertEqual(self.worker.cancelled_count, 1)

    async def test_cancel_unknown_task(self):
        result = await self.worker.cancel_task("unknown")

        self.assertFalse(result)
        self.assertEqual(self.worker.cancelled_count, 0)

    async def test_cancel_before_execution(self):
        self.send_task("immediate")

        result = await self.worker.cancel_task("immediate")

        self.assertTrue(result)
        self.assertEqual(len(self.worker.waiting), 0)
        self.assertEqual(len(self.worker.in_flight), 0)
        self.assertEqual(len(self.worker.task_map), 0)

    async def test_repeated_cancellation(self):
        self.send_task("repeat")

        first = await self.worker.cancel_task("repeat")
        second = await self.worker.cancel_task("repeat")

        self.assertTrue(first)
        self.assertFalse(second)
        self.assertEqual(self.worker.cancelled_count, 1)

    async def test_cancelled_task_cache(self):
        packet = self.send_task("cached")

        await self.worker.cancel_task("cached")

        self.worker.datagram_received(packet, ADDRESS)

        self.assertEqual(self.worker.duplicate_count, 1)
        self.assertEqual(len(self.worker.tasks), 0)

        self.transport.sendto.assert_called_with(
            self.worker.completed["cached"],
            ADDRESS,
        )

    async def test_graceful_shutdown(self):
        self.send_task("finish-1")
        self.send_task("finish-2")

        await self.worker.shutdown()

        self.assertTrue(self.worker.shutting_down)
        self.assertEqual(len(self.worker.tasks), 0)
        self.assertEqual(len(self.worker.completed), 2)
        self.assertEqual(self.worker.running, 0)

        self.transport.close.assert_called()

    async def test_shutdown_with_cancellation(self):
        self.send_task("cancel-1")
        self.send_task("cancel-2")

        await self.worker.shutdown(cancel_pending=True)

        self.assertEqual(self.worker.cancelled_count, 2)
        self.assertEqual(len(self.worker.tasks), 0)
        self.assertEqual(len(self.worker.waiting), 0)
        self.assertEqual(len(self.worker.in_flight), 0)

    async def test_reject_task_after_shutdown(self):
        await self.worker.shutdown()

        self.send_task("late-task")

        result = decode(
            self.transport.sendto.call_args.args[0]
        )

        self.assertFalse(result["ok"])
        self.assertEqual(
            result["error"],
            "Worker is shutting down",
        )


if __name__ == "__main__":
    unittest.main()
