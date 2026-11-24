import json
from datetime import datetime, timezone
from pathlib import Path


class RoutingDecisionLogger:

    def __init__(self, log_path):
        self.log_path = Path(log_path)
        self.log_path.parent.mkdir(parents=True, exist_ok=True)

    def record(
        self,
        task_id,
        node_id,
        decision,
        reason,
        local_score,
        peer=None,
    ):
        entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "task_id": task_id,
            "node_id": node_id,
            "decision": decision,
            "reason": reason,
            "local_load_score": local_score,
            "selected_peer": peer["node_id"] if peer else None,
            "peer_load_score": peer["load_score"] if peer else None,
        }

        with self.log_path.open("a", encoding="utf-8") as file:
            file.write(json.dumps(entry) + "\n")

        return entry
