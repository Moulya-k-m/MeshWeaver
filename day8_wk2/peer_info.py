
from dataclasses import dataclass
import time

from node_identity import validate_node_id


@dataclass
class PeerInfo:
    """
    Stores information about a peer in MeshWeaver.
    """

    node_id: str
    ip_address: str
    port: int
    last_seen: float

    def __post_init__(self):

        if not validate_node_id(self.node_id):
            raise ValueError("Invalid peer Node ID")

        if not isinstance(self.ip_address, str) or not self.ip_address:
            raise ValueError("Invalid IP address")

        if (
            not isinstance(self.port, int)
            or isinstance(self.port, bool)
            or not 1 <= self.port <= 65535
        ):
            raise ValueError("Invalid port number")

    def update_last_seen(self):
        """Update the peer's latest activity timestamp."""
        self.last_seen = time.time()

    def to_dict(self):
        """Convert peer information into a dictionary."""
        return {
            "node_id": self.node_id,
            "ip_address": self.ip_address,
            "port": self.port,
            "last_seen": self.last_seen
        }

    @classmethod
    def from_dict(cls, data):
        """Reconstruct a PeerInfo object from a dictionary."""
        return cls(
            node_id=data["node_id"],
            ip_address=data["ip_address"],
            port=data["port"],
            last_seen=data["last_seen"]
        )

    def display_info(self):
        """Display peer information."""
        print("Peer Information")
        print("----------------")
        print("Node ID:", self.node_id)
        print("IP Address:", self.ip_address)
        print("Port:", self.port)
        print("Last Seen:", self.last_seen)


if __name__ == "__main__":

    peer = PeerInfo(
        node_id="000000000000000000000000000000000000000a",
        ip_address="127.0.0.1",
        port=9001,
        last_seen=time.time()
    )

    peer.display_info()

    print("\nUpdating peer activity...")
    peer.update_last_seen()

    print("Updated Last Seen:", peer.last_seen)
