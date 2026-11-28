
import unittest

from day19_wk3.reliability_scheduler import ReliabilityAwareScheduler


class TestReliabilityAwareScheduler(unittest.TestCase):

    def setUp(self):
        reliability = {
            "NODE_A": {
                "completed": 98,
                "failed": 2,
                "total": 100,
                "success_rate": 98.0,
            },
            "NODE_B": {
                "completed": 90,
                "failed": 10,
                "total": 100,
                "success_rate": 90.0,
            },
            "NODE_C": {
                "completed": 65,
                "failed": 35,
                "total": 100,
                "success_rate": 65.0,
            },
        }

        execution_times = {
            "NODE_A": 2.0,
            "NODE_B": 1.0,
            "NODE_C": 3.0,
        }

        self.scheduler = ReliabilityAwareScheduler(
            reliability,
            execution_times
        )

        self.nodes = [
            {
                "node_id": "NODE_A",
                "cpu": 85,
                "ram": 70,
                "active_tasks": 5,
                "alive": True,
                "report_fresh": True,
            },
            {
                "node_id": "NODE_B",
                "cpu": 25,
                "ram": 30,
                "active_tasks": 2,
                "alive": True,
                "report_fresh": True,
            },
            {
                "node_id": "NODE_C",
                "cpu": 15,
                "ram": 20,
                "active_tasks": 1,
                "alive": True,
                "report_fresh": True,
            },
        ]

    def test_nodes_are_ranked(self):
        ranked = self.scheduler.rank_nodes(self.nodes)

        self.assertEqual(len(ranked), 3)

        scores = [node["score"] for node in ranked]

        self.assertEqual(scores, sorted(scores, reverse=True))

    def test_reliability_affects_selection(self):
        selected = self.scheduler.select_node(self.nodes)

        self.assertEqual(selected["node_id"], "NODE_B")

    def test_dead_nodes_are_excluded(self):
        nodes = self.nodes.copy()
        nodes[1] = {**nodes[1], "alive": False}

        ranked = self.scheduler.rank_nodes(nodes)

        self.assertNotIn(
            "NODE_B",
            [node["node_id"] for node in ranked]
        )

    def test_stale_reports_are_excluded(self):
        nodes = self.nodes.copy()
        nodes[1] = {**nodes[1], "report_fresh": False}

        ranked = self.scheduler.rank_nodes(nodes)

        self.assertNotIn(
            "NODE_B",
            [node["node_id"] for node in ranked]
        )

    def test_new_node_gets_neutral_reliability(self):
        score = self.scheduler._get_reliability("NEW_NODE")

        self.assertEqual(score, 50.0)

    def test_no_available_nodes(self):
        nodes = [
            {
                "node_id": "NODE_X",
                "cpu": 50,
                "ram": 50,
                "active_tasks": 1,
                "alive": False,
                "report_fresh": True,
            }
        ]

        self.assertIsNone(self.scheduler.select_node(nodes))

    def test_invalid_resource_values_are_excluded(self):
        nodes = [{
            "node_id": "NODE_X",
            "cpu": 120,
            "ram": 50,
            "active_tasks": 1,
            "alive": True,
            "report_fresh": True,
        }]

        self.assertEqual(self.scheduler.rank_nodes(nodes), [])

    def test_selection_contains_explanation(self):
        selected = self.scheduler.select_node(self.nodes)

        self.assertIn("Selected using reliability", selected["reason"])
        self.assertIn("components", selected)

    def test_invalid_cpu_string_is_excluded(self):
        nodes = [{
            "node_id": "NODE_X",
            "cpu": "unknown",
            "ram": 50,
            "active_tasks": 1,
            "alive": True,
            "report_fresh": True,
        }]

        self.assertEqual(self.scheduler.rank_nodes(nodes), [])

    def test_invalid_ram_string_is_excluded(self):
        nodes = [{
            "node_id": "NODE_X",
            "cpu": 50,
            "ram": "invalid",
            "active_tasks": 1,
            "alive": True,
            "report_fresh": True,
        }]

        self.assertEqual(self.scheduler.rank_nodes(nodes), [])

    def test_boolean_active_tasks_are_rejected(self):
        nodes = [{
            "node_id": "NODE_X",
            "cpu": 50,
            "ram": 50,
            "active_tasks": True,
            "alive": True,
            "report_fresh": True,
        }]

        self.assertEqual(self.scheduler.rank_nodes(nodes), [])

    def test_invalid_reliability_gets_neutral_score(self):
        self.scheduler.reliability_stats["NODE_X"] = {
            "total": 20,
            "success_rate": 150,
        }

        self.assertEqual(
            self.scheduler._get_reliability("NODE_X"),
            50.0
        )

    def test_missing_performance_gets_neutral_score(self):
        self.assertEqual(
            self.scheduler._get_performance("UNKNOWN_NODE"),
            50.0
        )


if __name__ == "__main__":
    unittest.main()
