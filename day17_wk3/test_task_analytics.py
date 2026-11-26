
import json
import pytest
from datetime import datetime, timezone, timedelta

from day17_wk3.task_analytics import TaskAnalytics


def create_event(task_id, status, node, timestamp):
    return {
        "task_id": task_id,
        "status": status,
        "node": node,
        "timestamp": timestamp.isoformat(),
        "result": None,
        "error": None
    }


def create_history(tmp_path):
    log_file = tmp_path / "history.jsonl"

    now = datetime.now(timezone.utc)

    events = [
        create_event("task-1", "SUBMITTED", "node-A", now),
        create_event("task-1", "ASSIGNED", "node-B", now + timedelta(seconds=2)),
        create_event("task-1", "COMPLETED", "node-B", now + timedelta(seconds=5)),

        create_event("task-2", "SUBMITTED", "node-A", now),
        create_event("task-2", "ASSIGNED", "node-C", now + timedelta(seconds=1)),
        create_event("task-2", "FAILED", "node-C", now + timedelta(seconds=4)),

        create_event("task-3", "SUBMITTED", "node-A", now),
    ]

    with log_file.open("w", encoding="utf-8") as file:
        for event in events:
            file.write(json.dumps(event) + "\n")

    return log_file


def test_load_events(tmp_path):
    log_file = create_history(tmp_path)

    analytics = TaskAnalytics(log_file)

    assert analytics.load_events() == 7


def test_task_summary(tmp_path):
    log_file = create_history(tmp_path)

    analytics = TaskAnalytics(log_file)
    analytics.load_events()

    summary = analytics.get_summary()

    assert summary["total_tasks"] == 3
    assert summary["completed"] == 1
    assert summary["failed"] == 1
    assert summary["pending"] == 1
    assert summary["success_rate"] == 50.0


def test_node_statistics(tmp_path):
    log_file = create_history(tmp_path)

    analytics = TaskAnalytics(log_file)
    analytics.load_events()

    stats = analytics.get_node_statistics()

    assert stats["node-B"]["completed"] == 1
    assert stats["node-C"]["failed"] == 1
    assert stats["node-A"]["other"] == 1


def test_average_execution_time(tmp_path):
    log_file = create_history(tmp_path)

    analytics = TaskAnalytics(log_file)
    analytics.load_events()

    assert analytics.get_average_execution_time() == 4.5


def test_empty_history(tmp_path):
    log_file = tmp_path / "empty.jsonl"
    log_file.touch()

    analytics = TaskAnalytics(log_file)
    analytics.load_events()

    summary = analytics.get_summary()

    assert summary["total_tasks"] == 0
    assert summary["success_rate"] == 0.0
    assert analytics.get_average_execution_time() == 0.0


def test_corrupted_history_is_ignored(tmp_path):
    log_file = create_history(tmp_path)

    with log_file.open("a", encoding="utf-8") as file:
        file.write("{invalid json}\n")

    analytics = TaskAnalytics(log_file)

    assert analytics.load_events() == 7


def test_missing_history_file(tmp_path):
    log_file = tmp_path / "missing.jsonl"

    analytics = TaskAnalytics(log_file)

    assert analytics.load_events() == 0
    assert analytics.get_summary()["total_tasks"] == 0


def test_failed_tasks_are_included_in_execution_time(tmp_path):
    log_file = tmp_path / "failure.jsonl"

    now = datetime.now(timezone.utc)

    events = [
        create_event("task-1", "SUBMITTED", "node-A", now),
        create_event("task-1", "FAILED", "node-B", now + timedelta(seconds=8))
    ]

    with log_file.open("w", encoding="utf-8") as file:
        for event in events:
            file.write(json.dumps(event) + "\n")

    analytics = TaskAnalytics(log_file)
    analytics.load_events()

    assert analytics.get_average_execution_time() == 8.0
