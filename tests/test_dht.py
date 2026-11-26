
import pytest

from meshweaver.dht import (
    DHT,
    RoutingTable,
    hash_node_id,
    xor_distance
)
from meshweaver.peer import Peer


class DummyNode:
    """Minimal node for isolated DHT tests."""

    def __init__(self, node_id):
        self.host = "127.0.0.1"
        self.port = 8888
        self.node_id = node_id
        self.peer_registry = {}

    def get_node_id(self):
        return self.node_id

    def add_peer(self, peer):
        if peer.node_id in self.peer_registry:
            raise ValueError("Duplicate peer")

        self.peer_registry[peer.node_id] = peer


def test_hash_node_id():
    first = hash_node_id("node-1")
    second = hash_node_id("node-1")

    assert first == second
    assert isinstance(first, int)


def test_different_ids_have_different_hashes():
    assert hash_node_id("node-1") != hash_node_id("node-2")


def test_xor_distance():
    distance = xor_distance("node-1", "node-2")

    assert distance > 0
    assert xor_distance("node-1", "node-1") == 0


def test_routing_table_initialization():
    table = RoutingTable("node-1")

    assert len(table) == 0
    assert len(table.buckets) == 256


def test_add_peer():
    table = RoutingTable("node-1")

    peer = Peer("node-2", "127.0.0.1", 8889)

    assert table.add_peer(peer)
    assert len(table) == 1


def test_self_is_not_added():
    table = RoutingTable("node-1")

    peer = Peer("node-1", "127.0.0.1", 8888)

    assert not table.add_peer(peer)
    assert len(table) == 0


def test_duplicate_peer_refresh():
    table = RoutingTable("node-1")

    peer1 = Peer("node-2", "127.0.0.1", 8889)
    peer2 = Peer("node-2", "127.0.0.1", 9999)

    assert table.add_peer(peer1)
    assert table.add_peer(peer2)

    assert len(table) == 1
    assert table.get_all_peers()[0].port == 9999


def test_find_closest():
    table = RoutingTable("node-1")

    peers = [
        Peer("node-2", "127.0.0.1", 8889),
        Peer("node-3", "127.0.0.1", 8890),
        Peer("node-4", "127.0.0.1", 8891)
    ]

    for peer in peers:
        table.add_peer(peer)

    closest = table.find_closest("node-2", count=2)

    assert len(closest) == 2
    assert closest[0].node_id == "node-2"


def test_remove_peer():
    table = RoutingTable("node-1")

    peer = Peer("node-2", "127.0.0.1", 8889)

    table.add_peer(peer)

    assert table.remove_peer("node-2")
    assert len(table) == 0


def test_remove_nonexistent_peer():
    table = RoutingTable("node-1")

    assert not table.remove_peer("unknown")


def test_bucket_capacity():
    table = RoutingTable("node-1", bucket_size=1)

    first = Peer("node-2", "127.0.0.1", 8889)

    table.add_peer(first)

    # Find another ID that maps to the same bucket.
    index = table.bucket_index(first.node_id)

    second_id = None

    for number in range(10000):
        candidate = f"candidate-{number}"

        if table.bucket_index(candidate) == index:
            second_id = candidate
            break

    assert second_id is not None

    second = Peer(second_id, "127.0.0.1", 8890)

    assert not table.add_peer(second)
    assert len(table) == 1


def test_dht_initialization():
    node = DummyNode("node-1")

    dht = DHT(node)

    assert dht.node_id == "node-1"
    assert len(dht.routing_table) == 0
    assert dht.storage == {}


def test_dht_local_storage():
    node = DummyNode("node-1")

    dht = DHT(node)

    dht.storage["test-key"] = "test-value"

    assert dht.storage["test-key"] == "test-value"


def test_dht_add_peer():
    node = DummyNode("node-1")

    dht = DHT(node)

    peer = Peer("node-2", "127.0.0.1", 8889)

    assert dht.add_peer(peer)
    assert len(dht.routing_table) == 1
    assert len(dht.get_peers()) == 1


def test_dht_rejects_self():
    node = DummyNode("node-1")

    dht = DHT(node)

    peer = Peer("node-1", "127.0.0.1", 8888)

    assert not dht.add_peer(peer)
    assert len(dht.routing_table) == 0
