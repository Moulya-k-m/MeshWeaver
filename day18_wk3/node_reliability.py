
import json
from pathlib import Path
from datetime import datetime


class NodeReliability:
    """Evaluate reliability and performance of distributed nodes."""

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

                    if (
                        isinstance(event, dict)
                        and event.get("task_id")
                        and event.get("status")
                    ):
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

    def get_node_reliability(self):
        """Calculate completed and failed tasks per node."""
        node_stats = {}

        for task in self._latest_tasks().values():
            node = task.get("node")

            if not node:
                continue

            if node not in node_stats:
                node_stats[node] = {
                    "completed": 0,
                    "failed": 0,
                    "total": 0,
                    "success_rate": 0.0,
                    "failure_rate": 0.0
                }

            status = task.get("status")

            if status == "COMPLETED":
                node_stats[node]["completed"] += 1

            elif status == "FAILED":
                node_stats[node]["failed"] += 1

        for stats in node_stats.values():
            total = stats["completed"] + stats["failed"]
            stats["total"] = total

            if total > 0:
                stats["success_rate"] = round(
                    stats["completed"] / total * 100, 2
                )

                stats["failure_rate"] = round(
                    stats["failed"] / total * 100, 2
                )

        return node_stats

    def get_node_execution_times(self):
        """Calculate average execution time for each node."""
        task_events = {}

        for event in self.events:
            task_id = event["task_id"]
            task_events.setdefault(task_id, []).append(event)

        node_durations = {}

        for events in task_events.values():
            submitted = next(
                (e for e in events if e["status"] == "SUBMITTED"),
                None
            )

            finished = next(
                (
                    e for e in reversed(events)
                    if e["status"] in ("COMPLETED", "FAILED")
                ),
                None
            )

            if not submitted or not finished:
                continue

            node = finished.get("node")

            if not node:
                continue

            try:
                start = datetime.fromisoformat(submitted["timestamp"])
                end = datetime.fromisoformat(finished["timestamp"])

                duration = (end - start).total_seconds()

                if duration >= 0:
                    node_durations.setdefault(node, []).append(duration)

            except (ValueError, TypeError, KeyError):
                continue

        averages = {}

        for node, durations in node_durations.items():
            averages[node] = round(
                sum(durations) / len(durations), 4
            )

        return averages

    def get_node_health(self, minimum_tasks=5):
        """Classify node health based on reliability."""
        if minimum_tasks < 1:
            raise ValueError("minimum_tasks must be at least 1")

        reliability = self.get_node_reliability()
        health = {}

        for node, stats in reliability.items():
            total = stats["total"]
            success_rate = stats["success_rate"]

            if total < minimum_tasks:
                status = "INSUFFICIENT_DATA"

            elif success_rate >= 90:
                status = "HEALTHY"

            elif success_rate >= 70:
                status = "WARNING"

            else:
                status = "CRITICAL"

            health[node] = {
                "health": status,
                "success_rate": success_rate,
                "total_tasks": total
            }

        return health

    def get_ranked_nodes(self):
        """Rank nodes by success rate and task count."""
        reliability = self.get_node_reliability()

        return sorted(
            reliability.items(),
            key=lambda item: (
                item[1]["success_rate"],
                item[1]["total"]
            ),
            reverse=True
        )
