
import time
from resource_monitor import load_score


class Scheduler:
    def __init__(self, peer_table, max_report_age=15.0):
        self.peer_table = peer_table
        self.max_report_age = max_report_age
        self.load_reports = {}

    def update_load(self, node_id, snapshot):
        """Store the latest resource report received from a node."""
        required = {"cpu", "ram", "active_tasks"}

        if not required.issubset(snapshot):
            raise ValueError("Incomplete resource snapshot")

        self.load_reports[node_id] = {
            "snapshot": snapshot.copy(),
            "received_at": time.monotonic()
        }

    def get_node_score(self, node_id):
        """Return a node's score, or None if its report is missing/stale."""
        report = self.load_reports.get(node_id)

        if report is None:
            return None

        age = time.monotonic() - report["received_at"]

        if age > self.max_report_age:
            return None

        return load_score(report["snapshot"])

    def choose_peer(self, exclude=None):
        """Choose the least-loaded ALIVE peer with a fresh load report."""
        candidates = []

        for node_id, peer in self.peer_table.peers.items():
            if node_id == exclude:
                continue

            if peer.state != "ALIVE":
                continue

            score = self.get_node_score(node_id)

            if score is not None:
                candidates.append((score, node_id, peer))

        if not candidates:
            return None

        _, node_id, peer = min(candidates, key=lambda item: item[0])

        return {
            "node_id": node_id,
            "host": peer.host,
            "tcp_port": peer.tcp_port,
            "load_score": self.get_node_score(node_id)
        }
