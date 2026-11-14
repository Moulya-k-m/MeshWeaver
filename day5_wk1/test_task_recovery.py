
import asyncio
from task_store import TaskStore


async def main():

    # First node: create and save a task
    store = TaskStore(
        node_id="NODE_A",
        journal_path="data/task_journal.jsonl"
    )

    task_id = await store.add(
        {"operation": "addition", "a": 10, "b": 20},
        task_id="T201"
    )

    task = await store.claim("WORKER_1")

    print("Before restart:", task.status)

    store.close()

    # Simulate node restart
    new_store = TaskStore(
        node_id="NODE_A",
        journal_path="data/task_journal.jsonl"
    )

    recovered_task = new_store.get(task_id)

    print("After restart:", recovered_task.status)
    print("Recovered task:", recovered_task.task_id)
    print("Pending queue:", list(new_store.pending))

    new_store.close()


asyncio.run(main())
