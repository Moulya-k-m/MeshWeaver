
import asyncio
import logging


def execute_task(payload):
    """Execute a supported task operation."""

    operation = payload.get("operation", "ECHO")
    a = payload.get("a", 0)
    b = payload.get("b", 0)

    if operation == "ADD":
        return a + b

    elif operation == "SUBTRACT":
        return a - b

    elif operation == "MULTIPLY":
        return a * b

    elif operation == "DIVIDE":
        if b == 0:
            raise ValueError("Division by zero")
        return a / b

    elif operation == "ECHO":
        return payload.get("value", payload)

    else:
        raise ValueError(f"Unsupported operation: {operation}")


async def worker_loop(store, node_id):

    worker_id = node_id

    logging.info("Worker started on node %s", node_id[:8])

    while True:
        try:
            task = await store.claim(worker_id, timeout=2.0)

            if task is None:
                continue

            logging.info("Picked up task %s", task.task_id)

            try:
                result = execute_task(task.payload)

                await store.complete(
                    task.task_id,
                    {"ok": True, "value": result}
                )

                logging.info(
                    "Task %s completed: %s",
                    task.task_id,
                    result
                )

            except Exception as exc:

                await store.fail(task.task_id, str(exc))

                logging.error(
                    "Task %s failed: %s",
                    task.task_id,
                    exc
                )

                current_task = store.get(task.task_id)

                if current_task.retries < current_task.max_retries:

                    delay = 2 ** current_task.retries

                    logging.info(
                        "Task %s will retry in %d seconds",
                        task.task_id,
                        delay
                    )

                    await asyncio.sleep(delay)

                retried = await store.retry(task.task_id)

                if retried:
                    current_task = store.get(task.task_id)

                    logging.info(
                        "Task %s requeued for retry (%d/%d)",
                        task.task_id,
                        current_task.retries,
                        current_task.max_retries,
                    )

                else:
                    logging.error(
                        "Task %s exhausted all retry attempts",
                        task.task_id,
                    )

        except asyncio.CancelledError:
            logging.info("Worker shutting down")
            raise
