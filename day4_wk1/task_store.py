
import asyncio
import time
import uuid

from collections import deque
from dataclasses import dataclass, field


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

    def __init__(self, node_id, max_retries=2):
        self.node_id = node_id
        self.max_retries = max_retries

        self.tasks = {}
        self.pending = deque()
        self.condition = asyncio.Condition()

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

            self.condition.notify_all()

        return task_id

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

            return task

    async def complete(self, task_id, result):

        async with self.condition:

            task = self.tasks.get(task_id)

            if task is None or task.status != "RUNNING":
                return False

            task.status = "COMPLETED"
            task.result = result
            task.error = None
            task.updated = time.time()

            self.condition.notify_all()

            return True

    async def fail(self, task_id, error):

        async with self.condition:

            task = self.tasks.get(task_id)

            if task is None or task.status != "RUNNING":
                return False

            task.status = "FAILED"
            task.error = str(error)
            task.assigned_to = None
            task.updated = time.time()

            self.condition.notify_all()

            return True

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
            self.condition.notify_all()

            return True

    def get(self, task_id):
        return self.tasks.get(task_id)

    def active_count(self):
        return sum(
            task.status == "RUNNING"
            for task in self.tasks.values()
        )

    def stats(self):

        counts = {
            "PENDING": 0,
            "RUNNING": 0,
            "COMPLETED": 0,
            "FAILED": 0
        }

        for task in self.tasks.values():
            counts[task.status] += 1

        return counts

    async def requeue_from(self, node_id):

        async with self.condition:

            recovered = []

            for task in self.tasks.values():

                if (
                    task.status == "RUNNING"
                    and task.assigned_to == node_id
                ):
                    task.status = "PENDING"
                    task.assigned_to = None
                    task.updated = time.time()

                    self.pending.append(task.task_id)
                    recovered.append(task.task_id)

            if recovered:
                self.condition.notify_all()

            return len(recovered)
