
from task_analytics import TaskAnalytics


def main():
    analytics = TaskAnalytics(
        "day16_wk3/execution_history.jsonl"
    )

    loaded = analytics.load_events()

    print("\n========== MESHWEAVER TASK ANALYTICS ==========")

    if loaded == 0:
        print("No execution history found.")
        print("Run some tasks before generating analytics.")
        return

    summary = analytics.get_summary()

    print("\n--- TASK SUMMARY ---")
    for key, value in summary.items():
        print(f"{key.replace('_', ' ').title()}: {value}")

    print("\n--- NODE STATISTICS ---")
    node_stats = analytics.get_node_statistics()

    if not node_stats:
        print("No node information available.")
    else:
        for node, stats in node_stats.items():
            print(f"\n{node}")
            for status, count in stats.items():
                print(f"  {status.title()}: {count}")

    print("\n--- EXECUTION PERFORMANCE ---")
    average = analytics.get_average_execution_time()
    print(f"Average execution time: {average} seconds")

    print("\n===============================================")


if __name__ == "__main__":
    main()
