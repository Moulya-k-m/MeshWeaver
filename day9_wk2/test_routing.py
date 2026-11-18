
import unittest

from day9_wk2.peer import Peer
from day9_wk2.routing_table import (
    RoutingTable,
    generate_node_id,
    xor_distance
)


class TestRoutingTable(unittest.TestCase):

    def setUp(self):
        self.local_id = generate_node_id("local")
        self.routing = RoutingTable(self.local_id, k=3)

    def create_peer(self, name, port=9101):
        return Peer(
            generate_node_id(name),
            "127.0.0.1",
            port
        )

    def test_add_peer(self):
        peer = self.create_peer("peer1")
        self.assertEqual(self.routing.add_peer(peer), "added")

    def test_duplicate_peer(self):
        peer = self.create_peer("peer1")
        self.routing.add_peer(peer)

        duplicate = self.create_peer("peer1")
        self.assertEqual(
            self.routing.add_peer(duplicate), "refreshed"
        )

    def test_self_node(self):
        peer = Peer(self.local_id, "127.0.0.1", 9101)
        self.assertEqual(
            self.routing.add_peer(peer), "self_node"
        )

    def test_closest_nodes(self):
        peers = [
            self.create_peer("peer1"),
            self.create_peer("peer2"),
            self.create_peer("peer3")
        ]

        for peer in peers:
            self.routing.add_peer(peer)

        result = self.routing.get_closest_nodes(
            generate_node_id("target"), 2
        )

        self.assertEqual(len(result), 2)

    def test_xor_distance(self):
        a = generate_node_id("A")
        b = generate_node_id("B")

        self.assertEqual(
            xor_distance(a, b),
            xor_distance(b, a)
        )

    def test_statistics(self):
        self.routing.add_peer(self.create_peer("peer1"))

        stats = self.routing.get_statistics()

        self.assertEqual(stats["total_peers"], 1)


if __name__ == "__main__":
    unittest.main(verbosity=2)
