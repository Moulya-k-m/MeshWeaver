
import json
import tempfile
from pathlib import Path

from day6_wk1.recovery_audit import audit_journal, display_report


def test_recovery_report_contains_all_fields():

    records = [
        {
            "op": "task",
            "task": {
                "task_id": "T101",
                "status": "PENDING"
            }
        },
        {
            "op": "update",
            "task_id": "T101",
            "fields": {
                "status": "RUNNING"
            }
        },
        {
            "op": "task",
            "task": {
                "task_id": "T102",
                "status": "COMPLETED"
            }
        }
    ]

    with tempfile.TemporaryDirectory() as temp_dir:

        path = Path(temp_dir) / "journal.jsonl"

        with open(path, "w", encoding="utf-8") as file:
            for record in records:
                file.write(json.dumps(record) + "\n")

        report = audit_journal(path)

        assert report["total_tasks"] == 2
        assert report["total_events"] == 3
        assert report["statuses"]["RUNNING"] == 1
        assert report["statuses"]["COMPLETED"] == 1
        assert report["interrupted_tasks"] == ["T101"]
        assert report["malformed_entries"] == 0
        assert report["orphan_updates"] == 0
        assert report["duplicate_tasks"] == 0


def test_display_report(capsys):

    report = {
        "total_tasks": 1,
        "total_events": 1,
        "statuses": {"RUNNING": 1},
        "interrupted_tasks": ["T101"],
        "malformed_entries": 0,
        "orphan_updates": 0,
        "duplicate_tasks": 0
    }

    display_report(report)

    output = capsys.readouterr().out

    assert "MESHWEAVER RECOVERY AUDITOR" in output
    assert "T101" in output
    assert "Interrupted tasks: 1" in output
    assert "WARNING" in output
