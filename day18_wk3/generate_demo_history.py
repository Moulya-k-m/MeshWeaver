
import sys
from pathlib import Path

# Add the MeshWeaver project root to Python's import path.
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from day16_wk3.execution_tracker import ExecutionTracker


def generate_demo_history():
    """Generate isolated sample execution history for Day 18."""

    log_file = PROJECT_ROOT / "day18_wk3" / "demo_execution_history.jsonl"

    # Start with a clean demonstration history.
    if log_file.exists():
        log_file.unlink()

    tracker = ExecutionTracker(log_file)

    scenarios = {
        "node-A": ["COMPLETED"] * 5,
        "node-B": ["COMPLETED"] * 4 + ["FAILED"],
        "node-C": ["COMPLETED"] * 2 + ["FAILED"] * 3,
        "node-D": ["COMPLETED"]
    }

    for node, outcomes in scenarios.items():
        for index, outcome in enumerate(outcomes, start=1):
            task_id = tracker.submit(node=node)
            tracker.assign(task_id, node)

            if outcome == "COMPLETED":
                tracker.complete(
                    task_id,
                    node,
                    result=f"Demo task {index} completed"
                )
            else:
                tracker.fail(
                    task_id,
                    node,
                    error=f"Demo task {index} failed"
                )

    print("Demo execution history generated successfully!")
    print(f"File: {log_file}")
    print(f"Total tasks: {sum(len(v) for v in scenarios.values())}")


if __name__ == "__main__":
    generate_demo_history()
