
"""Automated tests for MeshWeaver execution metrics."""

import asyncio
import unittest

from meshweaver.metrics import TaskMetrics
from meshweaver.broker import start_worker, start_client


def square(number):
    return number * number


def fail_task():
    raise ValueError("Intentional test failure")


class MetricsTests(unittest.TestCase):

    def test_initial_metrics(self):
        metrics = TaskMetrics().snapshot()

        self.assertEqual(metrics["submitted"], 0)
        self.assertEqual(metrics["successful"], 0)
        self.assertEqual(metrics["failed"], 0)
        self.assertEqual(metrics["success_rate"], 0.0)

    def test_successful_task(self):
        metrics = TaskMetrics()

        metrics.record_submission()
        metrics.record_success(0.5)

        result = metrics.snapshot()

        self.assertEqual(result["successful"], 1)
        self.assertEqual(result["average_duration"], 0.5)

    def test_failed_task(self):
        metrics = TaskMetrics()

        metrics.record_submission()
        metrics.record_failure(0.2)

        self.assertEqual(metrics.snapshot()["failed"], 1)

    def test_retry_and_timeout(self):
        metrics = TaskMetrics()

        metrics.record_retry()
        metrics.record_timeout()

        result = metrics.snapshot()

        self.assertEqual(result["retries"], 1)
        self.assertEqual(result["timeouts"], 1)

    def test_success_rate(self):
        metrics = TaskMetrics()

        for _ in range(4):
            metrics.record_submission()

        for _ in range(3):
            metrics.record_success(0.1)

        metrics.record_failure(0.2)

        result = metrics.snapshot()

        self.assertEqual(result["success_rate"], 75.0)
        self.assertEqual(result["pending"], 0)
        self.assertAlmostEqual(
            result["average_duration"], 0.125
        )


class BrokerMetricsTests(unittest.IsolatedAsyncioTestCase):

    async def asyncSetUp(self):
        self.worker_transport, self.worker = (
            await start_worker(port=0)
        )

        port = self.worker_transport.get_extra_info(
            "sockname"
        )[1]

        self.client_transport, self.client = (
            await start_client(port=port)
        )

    async def asyncTearDown(self):
        self.client_transport.close()
        self.worker_transport.close()

    async def test_successful_submission(self):
        result = await self.client.submit(square, 5)

        self.assertEqual(result, 25)

        metrics = self.client.get_metrics()

        self.assertEqual(metrics["submitted"], 1)
        self.assertEqual(metrics["successful"], 1)

    async def test_failed_submission(self):
        with self.assertRaises(RuntimeError):
            await self.client.submit(fail_task)

        metrics = self.client.get_metrics()

        self.assertEqual(metrics["submitted"], 1)
        self.assertEqual(metrics["failed"], 1)

    async def test_timeout_metrics(self):
        self.worker_transport.close()

        await asyncio.sleep(0.05)

        with self.assertRaises(TimeoutError):
            await self.client.submit(
                square,
                5,
                timeout=0.2,
                retries=1,
            )

        metrics = self.client.get_metrics()

        self.assertEqual(metrics["submitted"], 1)
        self.assertEqual(metrics["failed"], 1)
        self.assertEqual(metrics["retries"], 1)
        self.assertEqual(metrics["timeouts"], 2)
        self.assertEqual(metrics["pending"], 0)

    async def test_health_check_not_counted_as_task(self):
        healthy = await self.client.check_health()

        self.assertTrue(healthy)

        self.assertEqual(
            self.client.get_metrics()["submitted"],
            0,
        )


if __name__ == "__main__":
    unittest.main()
