# peer_table.py
import time
from dataclasses import dataclass

@dataclass
class Peer:
    node_id: str
    host: str
    tcp_port: int
    last_seen: float
    state: str = "ALIVE"   # ALIVE | SUSPECT | DEAD

class PeerTable:
    def __init__(self, suspect_after=6.0, dead_after=15.0):
        self.peers: dict[str, Peer] = {}
        self.suspect_after = suspect_after
        self.dead_after = dead_after

    def update(self, node_id, host, tcp_port):
        now = time.monotonic()
        peer = self.peers.get(node_id)
        if peer is None:
            self.peers[node_id] = Peer(node_id, host, tcp_port, now)
            return "JOINED"
        was = peer.state
        peer.last_seen, peer.state = now, "ALIVE"
        return "RECOVERED" if was != "ALIVE" else None

    def sweep(self):
        """Update states; return list of (node_id, old, new) changes."""
        changes, now = [], time.monotonic()
        for p in self.peers.values():
            age = now - p.last_seen
            new = "DEAD" if age > self.dead_after else \
                  "SUSPECT" if age > self.suspect_after else "ALIVE"
            if new != p.state:
                changes.append((p.node_id, p.state, new))
                p.state = new
        return changes