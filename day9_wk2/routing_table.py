
import hashlib

from day9_wk2.peer import Peer

ID_BITS = 160
BUCKET_COUNT = 160


def generate_node_id(value):
    return hashlib.sha1(value.encode()).hexdigest()


def validate_node_id(node_id):
    if not isinstance(node_id, str) or len(node_id) != 40:
        raise ValueError("Node ID must be 40 hexadecimal characters")

    try:
        int(node_id, 16)
    except ValueError:
        raise ValueError("Invalid hexadecimal node ID")

    return node_id.lower()


def xor_distance(node_id_1, node_id_2):
    return int(validate_node_id(node_id_1), 16) ^ int(
        validate_node_id(node_id_2), 16
    )


class KBucket:

    def __init__(self, k=3):
        self.k = k
        self.nodes = []

    def add_node(self, peer):

        for existing in self.nodes:
            if existing.node_id == peer.node_id:
                self.nodes.remove(existing)
                peer.refresh()
                self.nodes.append(peer)
                return "refreshed"

        if len(self.nodes) < self.k:
            self.nodes.append(peer)
            return "added"

        return "full"

    def remove_node(self, node_id):
        self.nodes = [
            peer for peer in self.nodes
            if peer.node_id != node_id
        ]

    def get_nodes(self):
        return list(self.nodes)


class RoutingTable:

    def __init__(self, local_node_id, k=3):
        self.local_node_id = validate_node_id(local_node_id)
        self.k = k
        self.buckets = [
            KBucket(k) for _ in range(BUCKET_COUNT)
        ]

    def get_bucket_index(self, node_id):
        distance = xor_distance(self.local_node_id, node_id)

        if distance == 0:
            return None

        return distance.bit_length() - 1

    def add_peer(self, peer, ping_callback=None):

        if peer.node_id == self.local_node_id:
            return "self_node"

        index = self.get_bucket_index(peer.node_id)
        bucket = self.buckets[index]

        result = bucket.add_node(peer)

        if result != "full":
            return result

        oldest = bucket.nodes[0]

        if ping_callback and ping_callback(oldest):
            oldest.refresh()
            bucket.nodes.remove(oldest)
            bucket.nodes.append(oldest)
            return "old_peer_alive"

        bucket.remove_node(oldest.node_id)
        bucket.add_node(peer)

        return "replaced"

    def get_closest_nodes(self, target_node_id, count=3):

        if count <= 0:
            raise ValueError("Count must be positive")

        peers = self.get_all_peers()

        peers.sort(
            key=lambda peer: xor_distance(
                peer.node_id, target_node_id
            )
        )

        return peers[:count]

    def get_all_peers(self):
        peers = []

        for bucket in self.buckets:
            peers.extend(bucket.get_nodes())

        return peers

    def get_statistics(self):
        return {
            "total_peers": len(self.get_all_peers()),
            "active_buckets": sum(
                bool(bucket.nodes) for bucket in self.buckets
            ),
            "total_buckets": BUCKET_COUNT,
            "bucket_capacity": self.k
        }
