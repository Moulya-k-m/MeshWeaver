
"""MeshWeaver task broker and metrics demonstration."""

import asyncio

from meshweaver.broker import start_client, start_worker
from meshweaver.logging_config import setup_logging


def square(number):
    return number * number


def divide(a, b):
    return a / b


async def slow_square(number):
    await asyncio.sleep(0.3)
    return number * number


async def main():
    print("\n========== MeshWeaver Demo ==========\n")

    worker_transport, worker = await start_worker(port=0)

    port = worker_transport.get_extra_info("sockname")[1]

    client_transport, client = await start_client(port=port)

    try:
        print("1. Checking worker health...\n")

        healthy = await client.check_health(timeout=1.0)

        print(
            "Worker health:",
            "HEALTHY" if healthy else "UNAVAILABLE",
        )

        print("\n2. Testing concurrent tasks...\n")

        results = await asyncio.gather(
            *(client.submit(square, n) for n in (5, 10, 25))
        )

        print("\nConcurrent task results:", results)

        print("\n3. Testing remote error handling...\n")

        try:
            await client.submit(divide, 10, 0)

        except RuntimeError as exc:
            print("\nExpected remote error:", exc)

        print("\n4. Task Execution Metrics")
        print("--------------------------------")

        metrics = client.get_metrics()

        print("Total submitted:", metrics["submitted"])
        print("Successful tasks:", metrics["successful"])
        print("Failed tasks:", metrics["failed"])
        print("Pending tasks:", metrics["pending"])
        print("Retries:", metrics["retries"])
        print("Timeouts:", metrics["timeouts"])

        print(
            "Average completion time:",
            metrics["average_duration"],
            "seconds",
        )

        print(
            "Success rate:",
            f'{metrics["success_rate"]:.2f}%',
        )


        print("\n5. Duplicate Task Prevention")

        result = await client.submit(
            slow_square,
            7,
            timeout=0.1,
            retries=10,
        )

        print("Task result:", result)
        print("Duplicate packets handled:", worker.duplicate_count)
        print("Retry count:", client.get_metrics()["retries"])
        print("Active tasks:", len(worker.in_flight))

        print("\n6. Task Cancellation")

        submission = asyncio.create_task(
            client.submit(
                slow_square, 12,
                timeout=2.0,
                retries=0,
            )
        )

        for _ in range(100):
            if worker.task_map:
                break
            await asyncio.sleep(0.001)

        if not worker.task_map:
            await submission
            raise RuntimeError("No active task found")

        task_id = next(iter(worker.task_map))

        cancelled = await worker.cancel_task(task_id)

        try:
            await submission
        except RuntimeError as exc:
            print("Expected cancellation:", exc)

        print("Cancellation successful:", cancelled)
        print("Cancelled tasks:", worker.cancelled_count)
        print("Active tasks:", len(worker.in_flight))

        print("\n7. Graceful Worker Shutdown")

        await worker.shutdown()

        print("Worker shutting down:", worker.shutting_down)
        print("Remaining tasks:", len(worker.tasks))

        print("\n========== Demo Completed ==========\n")

    finally:
        client_transport.close()
        worker_transport.close()


if __name__ == "__main__":
    setup_logging()
    asyncio.run(main())
