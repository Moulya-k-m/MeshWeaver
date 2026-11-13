
import psutil
import time

# Prime CPU measurement
psutil.cpu_percent(interval=None)


def snapshot(active_tasks: int) -> dict:
    return {
        "cpu": psutil.cpu_percent(interval=None),
        "ram": psutil.virtual_memory().percent,
        "active_tasks": active_tasks,
        "timestamp": time.time(),
    }


def load_score(s: dict) -> float:
    """Lower score means a less-loaded node."""
    return (
        s["active_tasks"] * 20
        + s["cpu"] * 0.5
        + s["ram"] * 0.3
    )


if __name__ == "__main__":
    data = snapshot(active_tasks=0)

    print("Resource Snapshot:", data)
    print("Load Score:", load_score(data))
