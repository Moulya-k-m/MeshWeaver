
"""
Reliability-aware scheduling for MeshWeaver.

Combines historical node reliability with current resource availability
to rank eligible nodes and select the most suitable node.
"""


class ReliabilityAwareScheduler:
    """Rank eligible nodes using reliability and resource information."""

    WEIGHTS = {
        "reliability": 0.50,
        "cpu_availability": 0.25,
        "ram_availability": 0.15,
        "performance": 0.10,
    }

    def __init__(
        self,
        reliability_stats,
        execution_times,
        minimum_history_tasks=5
    ):
        self.reliability_stats = reliability_stats
        self.execution_times = execution_times
        self.minimum_history_tasks = minimum_history_tasks

        if (
            not isinstance(minimum_history_tasks, int)
            or isinstance(minimum_history_tasks, bool)
            or minimum_history_tasks < 1
        ):
            raise ValueError(
                "minimum_history_tasks must be a positive integer"
            )

    def _get_reliability(self, node_id):
        """Return historical success rate or a neutral score."""

        stats = self.reliability_stats.get(node_id)

        if not isinstance(stats, dict):
            return 50.0

        total = stats.get("total", 0)
        success_rate = stats.get("success_rate")

        if (
            not isinstance(total, (int, float))
            or isinstance(total, bool)
            or total < self.minimum_history_tasks
        ):
            return 50.0

        if (
            not isinstance(success_rate, (int, float))
            or isinstance(success_rate, bool)
            or not 0 <= success_rate <= 100
        ):
            return 50.0

        return float(success_rate)

    def _get_performance(self, node_id):
        """Give faster nodes a higher performance score."""

        valid_times = []

        for value in self.execution_times.values():
            if (
                isinstance(value, (int, float))
                and not isinstance(value, bool)
                and value > 0
            ):
                valid_times.append(float(value))

        node_time = self.execution_times.get(node_id)

        if (
            not isinstance(node_time, (int, float))
            or isinstance(node_time, bool)
            or node_time <= 0
            or not valid_times
        ):
            return 50.0

        fastest_time = min(valid_times)

        return min(100.0, (fastest_time / node_time) * 100)

    def _score_node(self, node):
        """Calculate a weighted score for one eligible node."""

        try:
            node_id = node["node_id"]
            cpu = float(node["cpu"])
            ram = float(node["ram"])
            active_tasks = node["active_tasks"]

        except (KeyError, TypeError, ValueError):
            return None

        if not isinstance(node_id, str) or not node_id.strip():
            return None

        if not 0 <= cpu <= 100 or not 0 <= ram <= 100:
            return None

        if (
            not isinstance(active_tasks, int)
            or isinstance(active_tasks, bool)
            or active_tasks < 0
        ):
            return None

        reliability = self._get_reliability(node_id)

        cpu_availability = 100.0 - cpu
        ram_availability = 100.0 - ram

        performance = self._get_performance(node_id)

        components = {
            "reliability": round(reliability, 2),
            "cpu_availability": round(cpu_availability, 2),
            "ram_availability": round(ram_availability, 2),
            "performance": round(performance, 2),
        }

        score = sum(
            components[name] * weight
            for name, weight in self.WEIGHTS.items()
        )

        return {
            "node_id": node_id,
            "score": round(score, 2),
            "components": components,
            "active_tasks": active_tasks,
            "reason": (
                f"Selected using reliability ({reliability:.1f}%), "
                f"CPU availability ({cpu_availability:.1f}%), "
                f"RAM availability ({ram_availability:.1f}%) "
                f"and execution performance ({performance:.1f}%)."
            ),
        }

    def rank_nodes(self, nodes):
        """Rank alive nodes with fresh reports from highest to lowest."""

        candidates = []

        for node in nodes:

            if not isinstance(node, dict):
                continue

            if not node.get("alive", False):
                continue

            if not node.get("report_fresh", False):
                continue

            required = {
                "node_id",
                "cpu",
                "ram",
                "active_tasks"
            }

            if not required.issubset(node):
                continue

            result = self._score_node(node)

            if result is not None:
                candidates.append(result)

        return sorted(
            candidates,
            key=lambda item: (
                -item["score"],
                item["active_tasks"],
                item["node_id"]
            )
        )

    def select_node(self, nodes):
        """Return the best eligible node, or None if none are available."""

        ranked = self.rank_nodes(nodes)

        if not ranked:
            return None

        return ranked[0]
