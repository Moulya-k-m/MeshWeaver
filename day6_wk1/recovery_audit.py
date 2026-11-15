import json
import argparse
import tempfile
import os
from collections import Counter


def audit_journal(path):

    tasks = {}
    events = Counter()

    malformed = 0
    orphan_updates = 0
    duplicate_tasks = 0

    with open(path, "r", encoding="utf-8") as file:

        for line in file:

            try:
                record = json.loads(line)

                operation = record.get("op")
                events[operation] += 1

                if operation == "task":

                    task = record["task"]
                    task_id = task["task_id"]

                    if task_id in tasks:
                        duplicate_tasks += 1

                    tasks[task_id] = task

                elif operation == "update":

                    task_id = record["task_id"]

                    if task_id not in tasks:
                        orphan_updates += 1
                        continue

                    tasks[task_id].update(record["fields"])

                else:
                    malformed += 1

            except (ValueError, KeyError, TypeError):
                malformed += 1

    statuses = Counter(
        task.get("status", "UNKNOWN")
        for task in tasks.values()
    )

    interrupted = [
        task_id
        for task_id, task in tasks.items()
        if task.get("status") == "RUNNING"
    ]

    report = {
        "total_tasks": len(tasks),
        "statuses": dict(statuses),
        "interrupted_tasks": interrupted,
        "malformed_entries": malformed,
        "orphan_updates": orphan_updates,
        "duplicate_tasks": duplicate_tasks,
        "total_events": sum(events.values())
    }

    return report


def display_report(report):

    print("\n" + "=" * 45)
    print("       MESHWEAVER RECOVERY AUDITOR")
    print("=" * 45)

    print("\nTOTAL TASKS:", report["total_tasks"])
    print("TOTAL JOURNAL EVENTS:", report["total_events"])

    print("\n--- TASK STATUS ---")

    for status, count in sorted(report["statuses"].items()):
        print(f"{status}: {count}")

    print("\n--- RECOVERY ANALYSIS ---")

    print("Interrupted tasks:", len(report["interrupted_tasks"]))

    for task_id in report["interrupted_tasks"]:
        print("  Needs recovery:", task_id)

    print("\n--- JOURNAL HEALTH ---")

    print("Malformed entries:", report["malformed_entries"])
    print("Orphan updates:", report["orphan_updates"])
    print("Duplicate task records:", report["duplicate_tasks"])

    if (
        report["malformed_entries"]
        or report["orphan_updates"]
        or report["duplicate_tasks"]
    ):
        print("\nWARNING: Journal issues detected!")

    elif report["interrupted_tasks"]:
        print("\nWARNING: Interrupted tasks need attention!")

    else:
        print("\nJOURNAL HEALTH: HEALTHY")

    print("=" * 45)


def run_demo():

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

    with tempfile.NamedTemporaryFile(
        mode="w",
        suffix=".jsonl",
        delete=False,
        encoding="utf-8"
    ) as file:

        for record in records:
            file.write(json.dumps(record) + "\n")

        file.write("{corrupted journal entry\n")
        demo_path = file.name

    try:
        report = audit_journal(demo_path)
        display_report(report)

    finally:
        os.remove(demo_path)


if __name__ == "__main__":

    parser = argparse.ArgumentParser(
        description="MeshWeaver Task Journal Auditor"
    )

    parser.add_argument("--journal", help="Path to the task journal")
    parser.add_argument("--demo", action="store_true", help="Run a sample audit")

    args = parser.parse_args()

    if args.demo:
        run_demo()

    elif args.journal:
        report = audit_journal(args.journal)
        display_report(report)

    else:
        parser.error("Provide --demo or --journal")