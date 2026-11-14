
import asyncio
import time
import uuid

from collections import deque
from dataclasses import dataclass, field, asdict

from journal import Journal


@dataclass
class Task:
    task_id: str
    payload: dict
    status: str = "PENDING"
    assigned_to: str | None = None
    result: object = None
    error: str | None = None
    retries: int = 0
    max_retries: int = 2
    hops: int = 0
    origin: str | None = None
    created: float = field(default_factory=time.time)
    updated: float = field(default_factory=time.time)


class TaskStore:

    def __init__(self, node_id, max_retries=2, journal_path=None):

        self.node_id = node_id
        self.max_retries = max_retries

        self.tasks = {}
        self.pending = deque()
        self.condition = asyncio.Condition()

        self.journal = None

        # Recovery counters used by node.py
        self.recovered = 0
        self.restored = 0

        # Initialize persistent Journal
        if journal_path:
            self.journal = Journal(journal_path)

            saved_tasks = self.journal.load()

            # Restore saved tasks
            for task_data in saved_tasks.values():

                try:
                    task = Task(**task_data)
                except (TypeError, ValueError):
                    continue

                self.restored += 1

                # A RUNNING task may have been interrupted
                if task.status == "RUNNING":

                    task.status = "PENDING"
                    task.assigned_to = None
                    task.updated = time.time()

                    self.recovered += 1

                    # Save recovered state in journal
                    self._save_task(task)

                self.tasks[task.task_id] = task

                if task.status == "PENDING":
                    self.pending.append(task.task_id)

    # Save task information
    def _save_task(self, task, is_new=False):

        if self.journal is None:
            return

        if is_new:
            record = {
                "op": "task",
                "task": asdict(task)
            }
        else:
            record = {
                "op": "update",
                "task_id": task.task_id,
                "fields": asdict(task)
            }

        self.journal.write(record)

    # Add a new task
    async def add(self, payload, task_id=None, hops=0, origin=None):

        task_id = task_id or uuid.uuid4().hex[:8]

        async with self.condition:

            if task_id in self.tasks:
                return task_id

            task = Task(
                task_id=task_id,
                payload=payload,
                max_retries=self.max_retries,
                hops=hops,
                origin=origin
            )

            self.tasks[task_id] = task
            self.pending.append(task_id)

            self._save_task(task, is_new=True)

            self.condition.notify_all()

        return task_id

    # Claim a pending task
    async def claim(self, worker_id, timeout=2.0):

        async with self.condition:

            try:
                await asyncio.wait_for(
                    self.condition.wait_for(
                        lambda: len(self.pending) > 0
                    ),
                    timeout
                )
            except asyncio.TimeoutError:
                return None

            task_id = self.pending.popleft()
            task = self.tasks[task_id]

            task.status = "RUNNING"
            task.assigned_to = worker_id
            task.updated = time.time()

            self._save_task(task)

            return task

    # Complete a task
    async def complete(self, task_id, result):

        async with self.condition:

            task = self.tasks.get(task_id)

            if task is None or task.status != "RUNNING":
                return False

            task.status = "COMPLETED"
            task.result = result
            task.error = None
            task.assigned_to = None
            task.updated = time.time()

            self._save_task(task)

            self.condition.notify_all()

            return True

    # Mark a task as failed
    async def fail(self, task_id, error):

        async with self.condition:

            task = self.tasks.get(task_id)

            if task is None or task.status != "RUNNING":
                return False

            task.status = "FAILED"
            task.error = str(error)
            task.assigned_to = None
            task.updated = time.time()

            self._save_task(task)

            self.condition.notify_all()

            return True

    # Retry a failed task
    async def retry(self, task_id):

        async with self.condition:

            task = self.tasks.get(task_id)

            if task is None or task.status != "FAILED":
                return False

            if task.retries >= task.max_retries:
                return False

            task.retries += 1
            task.status = "PENDING"
            task.error = None
            task.assigned_to = None
            task.updated = time.time()

            self.pending.append(task_id)

            self._save_task(task)

            self.condition.notify_all()

            return True

    # Get task details
    def get(self, task_id):
        return self.tasks.get(task_id)

    # Count currently running tasks
    def active_count(self):

        return sum(
            task.status == "RUNNING"
            for task in self.tasks.values()
        )

    # Get task statistics
    def stats(self):

        counts = {
            "PENDING": 0,
            "RUNNING": 0,
            "COMPLETED": 0,
            "FAILED": 0
        }

        for task in self.tasks.values():
            if task.status in counts:
                counts[task.status] += 1

        return counts

    # Recover tasks assigned to a failed node
    async def requeue_from(self, node_id):

        async with self.condition:

            recovered_tasks = []

            for task in self.tasks.values():

                if (
                    task.status == "RUNNING"
                    and task.assigned_to == node_id
                ):

                    task.status = "PENDING"
                    task.assigned_to = None
                    task.updated = time.time()

                    self.pending.append(task.task_id)
                    recovered_tasks.append(task.task_id)

                    self._save_task(task)

            if recovered_tasks:
                self.condition.notify_all()

            return len(recovered_tasks)

    # Close Journal safely
    def close(self):

        if self.journal is not None:
            self.journal.close()
            self.journal = None
