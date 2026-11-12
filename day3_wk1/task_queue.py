import asyncio, uuid, time
from collections import deque
from dataclasses import dataclass, field
@dataclass
class Task:
    task_id: str
    payload: dict
    status: str = "PENDING"
    assigned_to: str | None = None
    result: object = None
    created: float = field(default_factory=time.time)
class TaskQueue:
    def __init__(self):
        self._pending = deque()
        self._tasks: dict[str, Task] = {}
        self._cond = asyncio.Condition()

    async def requeue_from(self, node_id):
        async with self._cond:
            stuck = [
                t for t in self._tasks.values()
                if t.status == "RUNNING" and t.assigned_to == node_id
            ]

            stuck.sort(key=lambda t: t.created, reverse=True)

            for t in stuck:
                t.status = "PENDING"
                t.assigned_to = None
                self._pending.appendleft(t.task_id)

            if stuck:
                self._cond.notify_all()

            return len(stuck)

    async def add(self, payload: dict) -> str:
        task = Task(uuid.uuid4().hex[:8], payload)
        async with self._cond:
            self._tasks[task.task_id] = task
            self._pending.append(task.task_id)
            self._cond.notify()
        return task.task_id

    async def get(self, worker_id: str, timeout: float | None = 5.0):
        async with self._cond:
            try:
                await asyncio.wait_for(
                    self._cond.wait_for(lambda: len(self._pending) > 0),
                    timeout
                )
            except asyncio.TimeoutError:
                return None

            task = self._tasks[self._pending.popleft()]
            task.status = "RUNNING"
            task.assigned_to = worker_id
            return task

    async def complete(self, task_id: str, result=None) -> bool:
        async with self._cond:
            task = self._tasks.get(task_id)
            if task is None or task.status != "RUNNING":
                return False

            task.status = "DONE"
            task.result = result
            return True

    def stats(self) -> dict:
        counts = {"PENDING": 0, "RUNNING": 0, "DONE": 0}
        for task in self._tasks.values():
            counts[task.status] += 1
        return counts
