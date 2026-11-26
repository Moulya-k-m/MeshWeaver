
import json
from pathlib import Path
from datetime import datetime


class TaskAnalytics:
    """Analyze distributed task execution history."""

    def __init__(self, log_file="day16_wk3/execution_history.jsonl"):
        self.log_file = Path(log_file)
        self.events = []

    def load_events(self):
        """Load valid execution events from JSONL history."""
        self.events = []

        if not self.log_file.exists():
            return 0

        with self.log_file.open("r", encoding="utf-8") as file:
            for line in file:
                try:
                    event = json.loads(line)

                    if event.get("task_id") and event.get("status"):
                        self.events.append(event)

                except (json.JSONDecodeError, TypeError):
                    continue

        return len(self.events)

    def _latest_tasks(self):
        """Get the latest recorded state of each task."""
        tasks = {}

        for event in self.events:
            tasks[event["task_id"]] = event

        return tasks

    def get_summary(self):
        """Calculate overall task execution statistics."""
        tasks = self._latest_tasks()

        summary = {
            "total_tasks": len(tasks),
            "completed": 0,
            "failed": 0,
            "pending": 0,
            "success_rate": 0.0
        }

        for task in tasks.values():
            status = task["status"]

            if status == "COMPLETED":
                summary["completed"] += 1
            elif status == "FAILED":
                summary["failed"] += 1
            else:
                summary["pending"] += 1

        finished = summary["completed"] + summary["failed"]

        if finished:
            summary["success_rate"] = round(
                summary["completed"] / finished * 100, 2
            )

        return summary

    def get_node_statistics(self):
        """Calculate how many tasks each node handled."""
        node_stats = {}

        for task in self._latest_tasks().values():
            node = task.get("node")

            if not node:
                continue

            if node not in node_stats:
                node_stats[node] = {
                    "completed": 0,
                    "failed": 0,
                    "other": 0
                }

            status = task["status"]

            if status == "COMPLETED":
                node_stats[node]["completed"] += 1
            elif status == "FAILED":
                node_stats[node]["failed"] += 1
            else:
                node_stats[node]["other"] += 1

        return node_stats

    def get_average_execution_time(self):
        """Calculate average time from submission to final execution."""
        task_events = {}

        for event in self.events:
            task_id = event["task_id"]
            task_events.setdefault(task_id, []).append(event)

        durations = []

        for events in task_events.values():
            submitted = next(
                (e for e in events if e["status"] == "SUBMITTED"),
                None
            )

            finished = next(
                (e for e in reversed(events)
                 if e["status"] in ("COMPLETED", "FAILED")),
                None
            )

            if not submitted or not finished:
                continue

            try:
                start = datetime.fromisoformat(submitted["timestamp"])
                end = datetime.fromisoformat(finished["timestamp"])

                duration = (end - start).total_seconds()

                if duration >= 0:
                    durations.append(duration)

            except (ValueError, TypeError, KeyError):
                continue

        if not durations:
            return 0.0

        return round(sum(durations) / len(durations), 4)
