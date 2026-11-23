
from dataclasses import dataclass


@dataclass
class Peer:
    """Stores connection information about another MeshWeaver node."""

    node_id: str
    host: str
    port: int

    def __post_init__(self):
        if not isinstance(self.node_id, str) or not self.node_id.strip():
            raise ValueError("Node ID must be a non-empty string")

        if not isinstance(self.host, str) or not self.host.strip():
            raise ValueError("Host must be a non-empty string")

        if isinstance(self.port, bool) or not isinstance(self.port, int):
            raise ValueError("Port must be an integer")

        if not 1 <= self.port <= 65535:
            raise ValueError("Port must be between 1 and 65535")


class PeerRegistry:
    """Maintains a collection of known MeshWeaver peers."""

    def __init__(self):
        self.peers = {}

    def add_peer(self, peer):
        """Register a new peer."""
        if not isinstance(peer, Peer):
            raise TypeError("Expected a Peer object")

        if peer.node_id in self.peers:
            raise ValueError(f"Peer already exists: {peer.node_id}")

        self.peers[peer.node_id] = peer

    def get_peer(self, node_id):
        """Retrieve a peer using its node ID."""
        return self.peers.get(node_id)

    def remove_peer(self, node_id):
        """Remove a peer using its node ID."""
        return self.peers.pop(node_id, None) is not None

    def get_all_peers(self):
        """Return all registered peers."""
        return list(self.peers.values())

    def __len__(self):
        return len(self.peers)
