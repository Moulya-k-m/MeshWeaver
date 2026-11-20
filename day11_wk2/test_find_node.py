
import asyncio
import unittest

from day9_wk2.peer import Peer
from day9_wk2.routing_table import (
    RoutingTable,
    generate_node_id
)
from day11_wk2.find_node import (
    FindNodeServer,
    FindNodeClient
)


class TestFindNode(unittest.IsolatedAsyncioTestCase):

    async def asyncSetUp(self):

        self.server_node_id = generate_node_id("server")

        self.routing_table = RoutingTable(
            self.server_node_id,
            k=20
        )

        self.test_peers = []

        for i in range(5):
            peer = Peer(
                node_id=generate_node_id(f"peer-{i}"),
                ip="127.0.0.1",
                port=9001 + i
            )

            self.test_peers.append(peer)
            self.routing_table.add_peer(peer)

        self.find_server = FindNodeServer(
            "127.0.0.1",
            0,
            self.server_node_id,
            self.routing_table
        )

        self.server = await asyncio.start_server(
            self.find_server.handle_client,
            self.find_server.host,
            self.find_server.port
        )

        self.port = self.server.sockets[0].getsockname()[1]

        self.client = FindNodeClient()

    async def asyncTearDown(self):
        self.server.close()
        await self.server.wait_closed()

    async def test_find_node_returns_peers(self):

        target_id = generate_node_id("target")

        result = await self.client.find_node(
            "127.0.0.1",
            self.port,
            target_id
        )

        self.assertTrue(len(result) > 0)

        for peer in result:
            self.assertIsInstance(peer, Peer)

    async def test_returns_closest_peers(self):

        target_id = generate_node_id("target")

        result = await self.client.find_node(
            "127.0.0.1",
            self.port,
            target_id
        )

        expected = self.routing_table.get_closest_nodes(
            target_id,
            count=20
        )

        self.assertEqual(
            [peer.node_id for peer in result],
            [peer.node_id for peer in expected]
        )

    async def test_invalid_target_id(self):

        result = await self.client.find_node(
            "127.0.0.1",
            self.port,
            "invalid-id"
        )

        self.assertEqual(result, [])

    async def test_unavailable_server(self):

        result = await self.client.find_node(
            "127.0.0.1",
            1,
            generate_node_id("target")
        )

        self.assertEqual(result, [])


if __name__ == "__main__":
    unittest.main()
