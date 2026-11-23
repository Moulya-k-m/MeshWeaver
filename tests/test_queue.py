
"""Tests for worker queue and concurrency management."""

import asyncio
import unittest
from unittest.mock import Mock

from meshweaver.broker import Worker, decode
from tests.test_deduplication import create_packet, slow_square, ADDRESS


class QueueTests(unittest.IsolatedAsyncioTestCase):

    async def asyncSetUp(self):
        self.worker = Worker(
            max_concurrent=2,
            max_queue=3,
        )
        self.transport = Mock()
        self.worker.connection_made(self.transport)

    async def asyncTearDown(self):
        if self.worker.tasks:
            await asyncio.gather(
                *list(self.worker.tasks),
                return_exceptions=True,
            )

    async def finish_tasks(self):
        if self.worker.tasks:
            await asyncio.gather(
                *list(self.worker.tasks)
            )

    def send_task(self, task_id):
        packet = create_packet(
            task_id, slow_square, 5
        )
        self.worker.datagram_received(
            packet, ADDRESS
        )
        return packet

    def responses(self):
        return [
            decode(call.args[0])
            for call in self.transport.sendto.call_args_list
        ]

    async def test_initial_queue_stats(self):
        stats = self.worker.get_queue_stats()

        self.assertEqual(stats["waiting"], 0)
        self.assertEqual(stats["running"], 0)
        self.assertEqual(stats["max_concurrent"], 2)
        self.assertEqual(stats["max_queue"], 3)

    async def test_concurrency_limit(self):
        for number in range(5):
            self.send_task(f"limit-{number}")

        await asyncio.sleep(0.01)

        stats = self.worker.get_queue_stats()

        self.assertEqual(stats["running"], 2)
        self.assertEqual(stats["waiting"], 3)

        await self.finish_tasks()

        stats = self.worker.get_queue_stats()

        self.assertEqual(stats["running"], 0)
        self.assertEqual(stats["waiting"], 0)
        self.assertLessEqual(
            stats["max_running_observed"], 2
        )

    async def test_queue_full(self):
        for number in range(6):
            self.send_task(f"full-{number}")

        stats = self.worker.get_queue_stats()

        self.assertEqual(stats["rejected"], 1)

        rejected = [
            response
            for response in self.responses()
            if response.get("error")
            == "Worker queue is full"
        ]

        self.assertEqual(len(rejected), 1)

        await self.finish_tasks()

    async def test_duplicate_not_queued_twice(self):
        packet = self.send_task("duplicate-queue")

        self.worker.datagram_received(
            packet, ADDRESS
        )

        stats = self.worker.get_queue_stats()

        self.assertEqual(stats["waiting"], 1)
        self.assertEqual(stats["duplicates"], 1)

        await self.finish_tasks()

    async def test_all_tasks_complete(self):
        for number in range(5):
            self.send_task(f"complete-{number}")

        await self.finish_tasks()

        stats = self.worker.get_queue_stats()

        self.assertEqual(len(self.worker.completed), 5)
        self.assertEqual(stats["waiting"], 0)
        self.assertEqual(stats["running"], 0)

    async def test_invalid_configuration(self):
        with self.assertRaises(ValueError):
            Worker(max_concurrent=0)

        with self.assertRaises(ValueError):
            Worker(max_queue=-1)


if __name__ == "__main__":
    unittest.main()
