"""Task lifecycle tracking for MeshWeaver."""

from collections import OrderedDict
from datetime import datetime, timezone
from enum import Enum


class TaskState(str, Enum):
    SUBMITTED = "SUBMITTED"
    QUEUED = "QUEUED"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"


class TaskRegistry:

    TERMINAL = {
        TaskState.COMPLETED,
        TaskState.FAILED,
        TaskState.CANCELLED,
    }

    TRANSITIONS = {
        TaskState.SUBMITTED: {
            TaskState.QUEUED,
            TaskState.FAILED,
            TaskState.CANCELLED,
        },
        TaskState.QUEUED: {
            TaskState.RUNNING,
            TaskState.FAILED,
            TaskState.CANCELLED,
        },
        TaskState.RUNNING: TERMINAL,
    }

    def __init__(self, max_history=256):
        if max_history < 1:
            raise ValueError("max_history must be positive")

        self.max_history = max_history
        self.active = {}
        self.history = OrderedDict()
        self.owners = {}

    @staticmethod
    def now():
        return datetime.now(timezone.utc).isoformat()

    def create(self, task_id, owner=None):
        if task_id in self.active:
            raise ValueError("Task already exists")

        self.history.pop(task_id, None)
        self.owners[task_id] = owner

        timestamp = self.now()

        self.active[task_id] = {
            "task_id": task_id,
            "state": TaskState.SUBMITTED.value,
            "submitted_at": timestamp,
            "updated_at": timestamp,
            "started_at": None,
            "completed_at": None,
            "error": None,
        }

    def transition(self, task_id, state, error=None):
        state = TaskState(state)
        record = self.active.get(task_id)

        if record is None:
            return False

        current = TaskState(record["state"])

        if state not in self.TRANSITIONS.get(current, set()):
            return False

        timestamp = self.now()

        record["state"] = state.value
        record["updated_at"] = timestamp

        if state == TaskState.RUNNING:
            record["started_at"] = timestamp

        if state in self.TERMINAL:
            record["completed_at"] = timestamp
            record["error"] = error

            self.history[task_id] = self.active.pop(task_id)

            while len(self.history) > self.max_history:
                expired_id, _ = self.history.popitem(last=False)
                self.owners.pop(expired_id, None)

        return True

    def get(self, task_id):
        record = self.active.get(task_id)

        if record is None:
            record = self.history.get(task_id)

        return dict(record) if record is not None else None

    def get_owner(self, task_id):
        """Return the registered task owner."""
        return self.owners.get(task_id)

    def snapshot(self):
        counts = {state.value: 0 for state in TaskState}

        for record in self.active.values():
            counts[record["state"]] += 1

        for record in self.history.values():
            counts[record["state"]] += 1

        return counts
