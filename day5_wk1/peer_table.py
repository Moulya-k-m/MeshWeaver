
import time
from dataclasses import dataclass


@dataclass
class Peer:
    node_id: str
    host: str
    tcp_port: int
    last_seen: float
    state: str = "ALIVE"
    direct: bool = True


class PeerTable:

    def __init__(self, suspect_after=6.0, dead_after=15.0):
        self.peers: dict[str, Peer] = {}
        self.suspect_after = suspect_after
        self.dead_after = dead_after

    def update(self, node_id, host, tcp_port):
        """Record a peer that this node directly discovered."""

        now = time.monotonic()
        peer = self.peers.get(node_id)

        if peer is None:
            self.peers[node_id] = Peer(
                node_id, host, tcp_port, now,
                state="ALIVE",
                direct=True
            )
            return "JOINED"

        was = peer.state

        peer.host = host
        peer.tcp_port = tcp_port
        peer.last_seen = now
        peer.state = "ALIVE"
        peer.direct = True

        return "RECOVERED" if was != "ALIVE" else None

    def learn_indirect(self, node_id, host, tcp_port):
        """Learn about a peer through another peer's announcement."""

        if node_id in self.peers:
            peer = self.peers[node_id]

            # Do not let indirect information refresh direct liveness.
            if peer.direct:
                return None

            peer.host = host
            peer.tcp_port = tcp_port
            return None

        self.peers[node_id] = Peer(
            node_id=node_id,
            host=host,
            tcp_port=tcp_port,
            last_seen=0,
            state="UNKNOWN",
            direct=False
        )

        return "LEARNED"

    def alive_peers(self):
        """Return peers directly confirmed to be alive."""

        return [
            peer for peer in self.peers.values()
            if peer.direct and peer.state == "ALIVE"
        ]

    def gossip_peers(self):
        """Return known peers suitable for sharing with other nodes."""

        return [
            {
                "node_id": peer.node_id,
                "host": peer.host,
                "tcp_port": peer.tcp_port
            }
            for peer in self.peers.values()
            if peer.state != "DEAD"
        ]

    def sweep(self):
        """Update liveness only for directly discovered peers."""

        changes = []
        now = time.monotonic()

        for peer in self.peers.values():

            if not peer.direct:
                continue

            age = now - peer.last_seen

            if age > self.dead_after:
                new_state = "DEAD"
            elif age > self.suspect_after:
                new_state = "SUSPECT"
            else:
                new_state = "ALIVE"

            if new_state != peer.state:
                changes.append((
                    peer.node_id,
                    peer.state,
                    new_state
                ))

                peer.state = new_state

        return changes
