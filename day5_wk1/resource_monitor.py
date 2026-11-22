import psutil
import time


# Prime CPU measurement
psutil.cpu_percent(interval=None)


def snapshot(active_tasks: int = 0) -> dict:
    """
    Collect current resource usage of the local node.

    Args:
        active_tasks: Number of currently running tasks.

    Returns:
        Dictionary containing CPU, RAM, active tasks and timestamp.
    """

    return {
        "cpu": psutil.cpu_percent(interval=None),
        "ram": psutil.virtual_memory().percent,
        "active_tasks": active_tasks,
        "timestamp": time.time(),
    }


def load_score(s: dict) -> float:
    """
    Calculate the resource load score of a node.

    Lower score means a less-loaded node.
    """

    return (
        s["active_tasks"] * 20
        + s["cpu"] * 0.5
        + s["ram"] * 0.3
    )


if __name__ == "__main__":

    data = snapshot(active_tasks=0)

    print("Resource Snapshot:", data)
    print("Load Score:", load_score(data))