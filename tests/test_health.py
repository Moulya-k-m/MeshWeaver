
"""Tests for MeshWeaver worker health monitoring."""

import asyncio
import unittest

from meshweaver.broker import start_client, start_worker


class HealthTests(unittest.IsolatedAsyncioTestCase):

    async def test_worker_healthy(self):
        worker_transport, _ = await start_worker(port=0)

        port = worker_transport.get_extra_info(
            "sockname"
        )[1]

        client_transport, client = await start_client(
            port=port
        )

        try:
            healthy = await client.check_health(
                timeout=1.0
            )

            self.assertTrue(healthy)

        finally:
            client_transport.close()
            worker_transport.close()

    async def test_worker_unavailable(self):
        worker_transport, _ = await start_worker(port=0)

        port = worker_transport.get_extra_info(
            "sockname"
        )[1]

        client_transport, client = await start_client(
            port=port
        )

        try:
            worker_transport.close()

            await asyncio.sleep(0.05)

            healthy = await client.check_health(
                timeout=0.2
            )

            self.assertFalse(healthy)

        finally:
            client_transport.close()
            worker_transport.close()

    async def test_invalid_timeout(self):
        worker_transport, _ = await start_worker(port=0)

        port = worker_transport.get_extra_info(
            "sockname"
        )[1]

        client_transport, client = await start_client(
            port=port
        )

        try:
            with self.assertRaises(ValueError):
                await client.check_health(timeout=0)

        finally:
            client_transport.close()
            worker_transport.close()


if __name__ == "__main__":
    unittest.main()
