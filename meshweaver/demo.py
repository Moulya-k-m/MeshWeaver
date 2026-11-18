"""Run the trusted localhost broker demonstration."""
import asyncio
from meshweaver.broker import start_client, start_worker


def square(number):
    return number * number


def divide(a, b):
    return a / b


async def main():
    worker_transport, _ = await start_worker()
    client_transport, client = await start_client()
    try:
        results = await asyncio.gather(*(client.submit(square, n) for n in (5, 10, 25)))
        print("Concurrent task results:", results)
        try:
            await client.submit(divide, 10, 0)
        except RuntimeError as exc:
            print("Expected remote error:", exc)
    finally:
        client_transport.close()
        worker_transport.close()


if __name__ == "__main__":
    asyncio.run(main())
