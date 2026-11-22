
"""Tests for duplicate task prevention."""

import asyncio
import base64
import unittest
from unittest.mock import Mock

import cloudpickle

from meshweaver.broker import Worker, encode, decode


ADDRESS = ("127.0.0.1", 12345)


async def slow_square(number):
    await asyncio.sleep(0.05)
    return number * number


def failing_task():
    raise ValueError("Intentional failure")


def create_packet(task_id, function, *args):
    payload = cloudpickle.dumps(
        (function, args, {})
    )

    return encode({
        "type": "task",
        "id": task_id,
        "payload": base64.b64encode(
            payload
        ).decode("ascii"),
    })


class DeduplicationTests(
    unittest.IsolatedAsyncioTestCase
):

    async def asyncSetUp(self):
        self.worker = Worker()
        self.transport = Mock()

        self.worker.connection_made(
            self.transport
        )

    async def asyncTearDown(self):
        if self.worker.tasks:
            await asyncio.gather(
                *list(self.worker.tasks),
                return_exceptions=True,
            )

    async def wait_for_tasks(self):
        if self.worker.tasks:
            await asyncio.gather(
                *list(self.worker.tasks)
            )

    def messages(self, message_type):
        return [
            decode(call.args[0])
            for call in self.transport.sendto.call_args_list
            if decode(call.args[0]).get("type")
            == message_type
        ]

    async def test_in_flight_duplicate(self):
        packet = create_packet(
            "task-001", slow_square, 5
        )

        self.worker.datagram_received(
            packet, ADDRESS
        )

        self.worker.datagram_received(
            packet, ADDRESS
        )

        self.assertEqual(
            len(self.worker.tasks), 1
        )

        self.assertEqual(
            self.worker.duplicate_count, 1
        )

        self.assertEqual(
            len(self.messages("ack")), 2
        )

        await self.wait_for_tasks()

        results = self.messages("result")

        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["value"], 25)

    async def test_completed_task_cache(self):
        packet = create_packet(
            "task-002", slow_square, 10
        )

        self.worker.datagram_received(
            packet, ADDRESS
        )

        await self.wait_for_tasks()

        original = self.worker.completed["task-002"]

        self.worker.datagram_received(
            packet, ADDRESS
        )

        self.assertEqual(
            len(self.worker.tasks), 0
        )

        self.assertEqual(
            self.worker.duplicate_count, 1
        )

        self.transport.sendto.assert_called_with(
            original, ADDRESS
        )

    async def test_unique_tasks(self):
        first = create_packet(
            "task-003", slow_square, 5
        )

        second = create_packet(
            "task-004", slow_square, 10
        )

        self.worker.datagram_received(
            first, ADDRESS
        )

        self.worker.datagram_received(
            second, ADDRESS
        )

        self.assertEqual(
            len(self.worker.tasks), 2
        )

        await self.wait_for_tasks()

        self.assertEqual(
            len(self.worker.completed), 2
        )

        self.assertEqual(
            self.worker.duplicate_count, 0
        )

    async def test_in_flight_cleanup(self):
        packet = create_packet(
            "task-005", slow_square, 5
        )

        self.worker.datagram_received(
            packet, ADDRESS
        )

        self.assertIn(
            "task-005", self.worker.in_flight
        )

        await self.wait_for_tasks()

        self.assertNotIn(
            "task-005", self.worker.in_flight
        )

        self.assertIn(
            "task-005", self.worker.completed
        )

    async def test_failed_task_is_cached(self):
        packet = create_packet(
            "task-006", failing_task
        )

        self.worker.datagram_received(
            packet, ADDRESS
        )

        await self.wait_for_tasks()

        self.assertNotIn(
            "task-006", self.worker.in_flight
        )

        result = decode(
            self.worker.completed["task-006"]
        )

        self.assertFalse(result["ok"])

        self.worker.datagram_received(
            packet, ADDRESS
        )

        self.assertEqual(
            self.worker.duplicate_count, 1
        )

        self.assertEqual(
            len(self.worker.tasks), 0
        )


if __name__ == "__main__":
    unittest.main()
