
import time
from dataclasses import dataclass, field


@dataclass
class Peer:

    node_id: str
    ip: str
    port: int
    last_seen: float = field(default_factory=time.time)

    def __post_init__(self):
        if len(self.node_id) != 40:
            raise ValueError("Node ID must be 40 characters")

        try:
            int(self.node_id, 16)
        except ValueError:
            raise ValueError("Invalid hexadecimal node ID")

        self.node_id = self.node_id.lower()

        if not self.ip:
            raise ValueError("IP address cannot be empty")

        if not isinstance(self.port, int) or not 1 <= self.port <= 65535:
            raise ValueError("Invalid port number")

    def refresh(self):
        self.last_seen = time.time()

    def to_dict(self):
        return {
            "node_id": self.node_id,
            "ip": self.ip,
            "port": self.port,
            "last_seen": self.last_seen
        }
