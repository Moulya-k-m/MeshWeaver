
import sys
from pathlib import Path

from node_reliability import NodeReliability


def display_report():
    # Use the file path supplied in the terminal.
    if len(sys.argv) > 1:
        log_file = Path(sys.argv[1])
    else:
        log_file = Path("day16_wk3/execution_history.jsonl")

    print("\n" + "=" * 55)
    print("       MESHWEAVER NODE RELIABILITY REPORT")
    print("=" * 55)

    print(f"\nHistory file: {log_file.resolve()}")

    monitor = NodeReliability(log_file)
    count = monitor.load_events()

    print(f"Execution events loaded: {count}")

    if count == 0:
        print("\nNo execution history available.")
        return

    reliability = monitor.get_node_reliability()
    execution_times = monitor.get_node_execution_times()
    health = monitor.get_node_health()
    ranked_nodes = monitor.get_ranked_nodes()

    print("\n--- NODE RELIABILITY ---")

    for node, stats in reliability.items():
        print(f"\nNode: {node}")
        print(f"  Completed tasks : {stats['completed']}")
        print(f"  Failed tasks    : {stats['failed']}")
        print(f"  Success rate    : {stats['success_rate']}%")
        print(f"  Failure rate    : {stats['failure_rate']}%")

    print("\n--- NODE EXECUTION TIMES ---")

    for node, duration in execution_times.items():
        print(f"{node}: {duration} seconds")

    print("\n--- NODE HEALTH STATUS ---")

    for node, details in health.items():
        print(
            f"{node}: {details['health']} "
            f"({details['success_rate']}% success)"
        )

    print("\n--- NODE PERFORMANCE RANKING ---")

    for position, (node, stats) in enumerate(ranked_nodes, start=1):
        print(
            f"{position}. {node} - "
            f"{stats['success_rate']}% success rate"
        )

    print("\n" + "=" * 55)
    print("          END OF RELIABILITY REPORT")
    print("=" * 55)


if __name__ == "__main__":
    display_report()
