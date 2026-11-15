import json
import tempfile
from pathlib import Path

from day6_wk1.recovery_audit import audit_journal


def test_detects_malformed_journal_entry():

    records = [
        {
            "op": "task",
            "task": {
                "task_id": "T101",
                "status": "PENDING"
            }
        }
    ]

    with tempfile.TemporaryDirectory() as temp_dir:

        path = Path(temp_dir) / "journal.jsonl"

        with open(path, "w", encoding="utf-8") as file:
            for record in records:
                file.write(json.dumps(record) + "\n")

            file.write("{invalid json entry\n")

        report = audit_journal(path)

        assert report["malformed_entries"] == 1
        assert report["total_tasks"] == 1


def test_detects_orphan_updates():

    records = [
        {
            "op": "update",
            "task_id": "T999",
            "fields": {
                "status": "RUNNING"
            }
        }
    ]

    with tempfile.TemporaryDirectory() as temp_dir:

        path = Path(temp_dir) / "journal.jsonl"

        with open(path, "w", encoding="utf-8") as file:
            for record in records:
                file.write(json.dumps(record) + "\n")

        report = audit_journal(path)

        assert report["orphan_updates"] == 1
        assert report["total_tasks"] == 0


def test_detects_duplicate_task_records():

    records = [
        {
            "op": "task",
            "task": {
                "task_id": "T101",
                "status": "PENDING"
            }
        },
        {
            "op": "task",
            "task": {
                "task_id": "T101",
                "status": "RUNNING"
            }
        }
    ]

    with tempfile.TemporaryDirectory() as temp_dir:

        path = Path(temp_dir) / "journal.jsonl"

        with open(path, "w", encoding="utf-8") as file:
            for record in records:
                file.write(json.dumps(record) + "\n")

        report = audit_journal(path)

        assert report["duplicate_tasks"] == 1
        assert report["total_tasks"] == 1