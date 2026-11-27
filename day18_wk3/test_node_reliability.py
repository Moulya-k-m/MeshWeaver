
import json
import pytest
from datetime import datetime, timezone, timedelta

from day18_wk3.node_reliability import NodeReliability


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

    events = []

    # Healthy node: 5 successful tasks
    for i in range(5):
        events.extend([
            create_event(
                f"healthy-{i}", "SUBMITTED", "node-A",
                now + timedelta(seconds=i * 10)
            ),
            create_event(
                f"healthy-{i}", "COMPLETED", "node-A",
                now + timedelta(seconds=i * 10 + 2)
            )
        ])

    # Warning node: 4 successful and 1 failed task
    for i in range(5):
        status = "FAILED" if i == 4 else "COMPLETED"

        events.extend([
            create_event(
                f"warning-{i}", "SUBMITTED", "node-B",
                now + timedelta(seconds=i * 10)
            ),
            create_event(
                f"warning-{i}", status, "node-B",
                now + timedelta(seconds=i * 10 + 3)
            )
        ])

    # Critical node: 2 successful and 3 failed tasks
    for i in range(5):
        status = "COMPLETED" if i < 2 else "FAILED"

        events.extend([
            create_event(
                f"critical-{i}", "SUBMITTED", "node-C",
                now + timedelta(seconds=i * 10)
            ),
            create_event(
                f"critical-{i}", status, "node-C",
                now + timedelta(seconds=i * 10 + 5)
            )
        ])

    # Insufficient history node
    events.extend([
        create_event("small-1", "SUBMITTED", "node-D", now),
        create_event(
            "small-1", "COMPLETED", "node-D",
            now + timedelta(seconds=4)
        )
    ])

    with log_file.open("w", encoding="utf-8") as file:
        for event in events:
            file.write(json.dumps(event) + "\n")

    return log_file


def test_load_events(tmp_path):
    log_file = create_history(tmp_path)

    monitor = NodeReliability(log_file)

    assert monitor.load_events() == 32


def test_node_reliability(tmp_path):
    monitor = NodeReliability(create_history(tmp_path))
    monitor.load_events()

    stats = monitor.get_node_reliability()

    assert stats["node-A"]["success_rate"] == 100.0
    assert stats["node-B"]["success_rate"] == 80.0
    assert stats["node-C"]["success_rate"] == 40.0

    assert stats["node-B"]["failure_rate"] == 20.0


def test_node_execution_times(tmp_path):
    monitor = NodeReliability(create_history(tmp_path))
    monitor.load_events()

    averages = monitor.get_node_execution_times()

    assert averages["node-A"] == 2.0
    assert averages["node-B"] == 3.0
    assert averages["node-C"] == 5.0


def test_node_health_classification(tmp_path):
    monitor = NodeReliability(create_history(tmp_path))
    monitor.load_events()

    health = monitor.get_node_health()

    assert health["node-A"]["health"] == "HEALTHY"
    assert health["node-B"]["health"] == "WARNING"
    assert health["node-C"]["health"] == "CRITICAL"
    assert health["node-D"]["health"] == "INSUFFICIENT_DATA"


def test_node_ranking(tmp_path):
    monitor = NodeReliability(create_history(tmp_path))
    monitor.load_events()

    ranked = monitor.get_ranked_nodes()

    names = [node for node, stats in ranked]

    assert names.index("node-A") < names.index("node-B")
    assert names.index("node-B") < names.index("node-C")


def test_missing_history_file(tmp_path):
    monitor = NodeReliability(tmp_path / "missing.jsonl")

    assert monitor.load_events() == 0
    assert monitor.get_node_reliability() == {}


def test_corrupted_history(tmp_path):
    log_file = create_history(tmp_path)

    with log_file.open("a", encoding="utf-8") as file:
        file.write("{invalid json}\n")

    monitor = NodeReliability(log_file)

    assert monitor.load_events() == 32


def test_invalid_minimum_tasks(tmp_path):
    monitor = NodeReliability(create_history(tmp_path))
    monitor.load_events()

    with pytest.raises(ValueError):
        monitor.get_node_health(minimum_tasks=0)
