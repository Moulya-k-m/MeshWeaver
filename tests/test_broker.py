import asyncio
import unittest
from meshweaver.broker import encode, decode, start_client, start_worker


def square(n):
    return n * n


def fail():
    raise ValueError("test failure")


class BrokerTests(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.worker_transport, _ = await start_worker(0)
        port = self.worker_transport.get_extra_info("sockname")[1]
        self.client_transport, self.client = await start_client(port)

    async def asyncTearDown(self):
        self.client_transport.close()
        self.worker_transport.close()
        await asyncio.sleep(0)

    async def test_concurrent_tasks(self):
        values = await asyncio.gather(*(self.client.submit(square, n) for n in range(6)))
        self.assertEqual(values, [0, 1, 4, 9, 16, 25])

    async def test_remote_error(self):
        with self.assertRaisesRegex(RuntimeError, "test failure"):
            await self.client.submit(fail)

    async def test_timeout(self):
        self.worker_transport.close()
        with self.assertRaises(TimeoutError):
            await self.client.submit(square, 3, timeout=0.05, retries=1)

    def test_invalid_message(self):
        with self.assertRaises(ValueError):
            decode(b'[]')
        with self.assertRaises(ValueError):
            encode({"payload": "x" * 61000})


if __name__ == "__main__":
    unittest.main()
