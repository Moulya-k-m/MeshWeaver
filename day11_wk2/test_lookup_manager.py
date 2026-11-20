
import unittest
from unittest.mock import AsyncMock

from day9_wk2.peer import Peer
from day9_wk2.routing_table import (
    RoutingTable,
    generate_node_id,
    xor_distance
)

from day11_wk2.lookup_manager import LookupManager


class TestLookupManager(unittest.IsolatedAsyncioTestCase):

    async def asyncSetUp(self):

        self.local_node_id = generate_node_id("local")

        self.routing_table = RoutingTable(
            self.local_node_id,
            k=20
        )

        self.peers = []

        for i in range(5):
            peer = Peer(
                node_id=generate_node_id(f"peer-{i}"),
                ip="127.0.0.1",
                port=9001 + i
            )

            self.peers.append(peer)
            self.routing_table.add_peer(peer)

        self.manager = LookupManager(
            self.local_node_id,
            self.routing_table,
            alpha=3,
            k=20
        )

    async def test_lookup_returns_peers(self):

        self.manager.client.find_node = AsyncMock(
            return_value=self.peers
        )

        result = await self.manager.lookup(
            generate_node_id("target")
        )

        self.assertTrue(len(result) > 0)

        for peer in result:
            self.assertIsInstance(peer, Peer)

    async def test_lookup_returns_closest_peers(self):

        target_id = generate_node_id("target")

        self.manager.client.find_node = AsyncMock(
            return_value=[]
        )

        result = await self.manager.lookup(target_id)

        distances = [
            xor_distance(peer.node_id, target_id)
            for peer in result
        ]

        self.assertEqual(distances, sorted(distances))

    async def test_lookup_discovers_new_peers(self):

        target_id = generate_node_id("target")

        new_peer = Peer(
            node_id=generate_node_id("new-peer"),
            ip="127.0.0.1",
            port=9100
        )

        self.manager.client.find_node = AsyncMock(
            return_value=[new_peer]
        )

        result = await self.manager.lookup(target_id)

        self.assertTrue(
            any(peer.node_id == new_peer.node_id for peer in result)
        )

    async def test_lookup_excludes_local_node(self):

        local_peer = Peer(
            node_id=self.local_node_id,
            ip="127.0.0.1",
            port=9200
        )

        self.manager.client.find_node = AsyncMock(
            return_value=[local_peer]
        )

        result = await self.manager.lookup(
            generate_node_id("target")
        )

        self.assertFalse(
            any(peer.node_id == self.local_node_id for peer in result)
        )

    async def test_invalid_target_id(self):

        with self.assertRaises(ValueError):
            await self.manager.lookup("invalid-id")


if __name__ == "__main__":
    unittest.main()
