
import pytest
from day16_wk3.execution_tracker import ExecutionTracker


def test_task_lifecycle(tmp_path):
    tracker = ExecutionTracker(tmp_path / "history.jsonl")

    task_id = tracker.submit("node-A")
    assert tracker.get_status(task_id) == "SUBMITTED"

    tracker.assign(task_id, "node-B")
    assert tracker.get_status(task_id) == "ASSIGNED"

    tracker.complete(task_id, "node-B", 42)
    assert tracker.get_task(task_id)["result"] == 42


def test_task_failure(tmp_path):
    tracker = ExecutionTracker(tmp_path / "history.jsonl")

    task_id = tracker.submit()
    tracker.fail(task_id, "node-B", "Execution timeout")

    assert tracker.get_status(task_id) == "FAILED"


def test_unknown_task_rejected(tmp_path):
    tracker = ExecutionTracker(tmp_path / "history.jsonl")

    with pytest.raises(ValueError):
        tracker.assign("invalid-id", "node-B")


def test_completed_task_cannot_be_reassigned(tmp_path):
    tracker = ExecutionTracker(tmp_path / "history.jsonl")

    task_id = tracker.submit()
    tracker.complete(task_id, "node-B", 100)

    with pytest.raises(ValueError):
        tracker.assign(task_id, "node-C")

def test_history_survives_restart(tmp_path):
    log_file = tmp_path / "history.jsonl"

    tracker1 = ExecutionTracker(log_file)
    task_id = tracker1.submit("node-A")
    tracker1.assign(task_id, "node-B")
    tracker1.complete(task_id, "node-B", 250)

    tracker2 = ExecutionTracker(log_file)
    restored = tracker2.load_history()

    assert restored == 3
    assert tracker2.get_status(task_id) == "COMPLETED"
    assert tracker2.get_task(task_id)["result"] == 250

def test_corrupted_history_entry_is_skipped(tmp_path):
    log_file = tmp_path / "history.jsonl"

    tracker1 = ExecutionTracker(log_file)
    task_id = tracker1.submit("node-A")

    with log_file.open("a", encoding="utf-8") as file:
        file.write("{invalid json entry}\n")

    tracker2 = ExecutionTracker(log_file)
    restored = tracker2.load_history()

    assert restored == 1
    assert tracker2.get_status(task_id) == "SUBMITTED"

def test_multiple_tasks_tracked_independently(tmp_path):
    tracker = ExecutionTracker(tmp_path / "history.jsonl")

    task1 = tracker.submit("node-A")
    task2 = tracker.submit("node-A")
    task3 = tracker.submit("node-C")

    tracker.assign(task1, "node-B")
    tracker.complete(task1, "node-B", 100)

    tracker.assign(task2, "node-C")
    tracker.fail(task2, "node-C", "Timeout")

    assert tracker.get_status(task1) == "COMPLETED"
    assert tracker.get_status(task2) == "FAILED"
    assert tracker.get_status(task3) == "SUBMITTED"

    assert len(tracker.get_all_tasks()) == 3
