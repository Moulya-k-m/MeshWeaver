
import json
import uuid
from datetime import datetime, timezone
from pathlib import Path


class ExecutionTracker:
    """Track the lifecycle of distributed tasks."""

    def __init__(self, log_file="day16_wk3/execution_history.jsonl"):
        self.log_file = Path(log_file)
        self.log_file.parent.mkdir(parents=True, exist_ok=True)

        self.tasks = {}

    def _record(self, task_id, status, node=None, result=None, error=None):
        event = {
            "task_id": task_id,
            "status": status,
            "node": node,
            "result": result,
            "error": error,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

        with self.log_file.open("a", encoding="utf-8") as file:
            file.write(json.dumps(event, default=str) + "\n")

        self.tasks[task_id] = event
        return event

    def submit(self, node=None):
        task_id = str(uuid.uuid4())

        self._record(task_id, "SUBMITTED", node=node)

        return task_id

    def assign(self, task_id, node):
        self._validate(task_id)
        return self._record(task_id, "ASSIGNED", node=node)

    def complete(self, task_id, node, result):
        self._validate(task_id)
        return self._record(
            task_id, "COMPLETED", node=node, result=result
        )

    def fail(self, task_id, node, error):
        self._validate(task_id)
        return self._record(
            task_id, "FAILED", node=node, error=str(error)
        )

    def _validate(self, task_id):
        if task_id not in self.tasks:
            raise ValueError(f"Unknown task ID: {task_id}")

        if self.tasks[task_id]["status"] in ("COMPLETED", "FAILED"):
            raise ValueError(f"Task {task_id} is already finished")

    def get_status(self, task_id):
        if task_id not in self.tasks:
            raise ValueError(f"Unknown task ID: {task_id}") 
      
        return self.tasks[task_id]["status"]

    def get_task(self, task_id):
        return self.tasks.get(task_id)

    def get_all_tasks(self):
        return self.tasks.copy()
    
    def load_history(self):
        """Restore the latest state of every task from the JSONL log."""
        if not self.log_file.exists():
            return 0

        restored = 0

        with self.log_file.open("r", encoding="utf-8") as file:
            for line in file:
                try:
                    event = json.loads(line)
                    task_id = event.get("task_id")

                    if task_id and event.get("status"):
                        self.tasks[task_id] = event
                        restored += 1

                except (json.JSONDecodeError, OSError):
                    continue

        return restored

