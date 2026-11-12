
import asyncio
from task_queue import TaskQueue


async def main():
    queue = TaskQueue()

    # Submit a task
    task_id = await queue.add({"job": "process_data"})
    print("Task submitted:", task_id)

    # Node 1 picks up the task
    task = await queue.get("Node-1")
    print("Assigned to:", task.assigned_to)

    # Simulate Node 1 failure
    recovered = await queue.requeue_from("Node-1")
    print("Tasks recovered:", recovered)

    # Node 2 picks up the recovered task
    retry = await queue.get("Node-2")

    print("Reassigned to:", retry.assigned_to)

    # Verify recovery
    assert recovered == 1
    assert retry.task_id == task_id
    assert retry.assigned_to == "Node-2"

    print("\nPASS: Task successfully recovered!")
    print("Queue status:", queue.stats())


if __name__ == "__main__":
    asyncio.run(main())
