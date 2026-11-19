
"""Run the trusted localhost broker demonstration."""

import asyncio

from meshweaver.broker import start_client, start_worker
from meshweaver.logging_config import setup_logging


def square(number):
    """Return the square of a number."""
    return number * number


def divide(a, b):
    """Divide two numbers."""
    return a / b


async def main():
    """Demonstrate concurrent remote task execution."""

    print("\n========== MeshWeaver Task Broker Demo ==========\n")

    # Start worker node
    worker_transport, _ = await start_worker()

    # Start client node
    client_transport, client = await start_client()

    try:
        print("1. Testing concurrent task execution...\n")

        # Submit three tasks concurrently
        results = await asyncio.gather(
            *(
                client.submit(square, n)
                for n in (5, 10, 25)
            )
        )

        print("\nConcurrent task results:", results)

        print("\n2. Testing remote error handling...\n")

        # Submit a task that intentionally raises an error
        try:
            await client.submit(divide, 10, 0)

        except RuntimeError as exc:
            print("\nExpected remote error:", exc)

        print("\n========== Demo Completed ==========\n")

    finally:
        # Close connections
        client_transport.close()
        worker_transport.close()


if __name__ == "__main__":

    # Enable MeshWeaver structured logging
    setup_logging()

    # Run asynchronous demonstration
    asyncio.run(main())
