
"""Run the trusted localhost MeshWeaver demonstration."""

import asyncio

from meshweaver.broker import start_client, start_worker
from meshweaver.logging_config import setup_logging


def square(number):
    return number * number


def divide(a, b):
    return a / b


async def main():
    print("\n========== MeshWeaver Task Broker Demo ==========\n")

    worker_transport, _ = await start_worker()
    client_transport, client = await start_client()

    try:
        # Check worker health
        print("1. Checking worker health...\n")

        healthy = await client.check_health(timeout=1.0)

        print(
            "\nWorker health:",
            "HEALTHY" if healthy else "UNAVAILABLE",
        )

        # Test concurrent task execution
        print("\n2. Testing concurrent task execution...\n")

        results = await asyncio.gather(
            *(
                client.submit(square, n)
                for n in (5, 10, 25)
            )
        )

        print("\nConcurrent task results:", results)

        # Test remote error handling
        print("\n3. Testing remote error handling...\n")

        try:
            await client.submit(divide, 10, 0)

        except RuntimeError as exc:
            print("\nExpected remote error:", exc)

        print("\n========== Demo Completed ==========\n")

    finally:
        client_transport.close()
        worker_transport.close()


if __name__ == "__main__":
    setup_logging()
    asyncio.run(main())
