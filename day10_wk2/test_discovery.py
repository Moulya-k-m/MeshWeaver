
import asyncio
import unittest

from day10_wk2.bootstrap import BootstrapServer
from day10_wk2.peer_discovery import PeerDiscovery


class TestPeerDiscovery(unittest.IsolatedAsyncioTestCase):

    async def asyncSetUp(self):
        self.bootstrap = BootstrapServer(
            host="127.0.0.1",
            port=0
        )

        self.server = await asyncio.start_server(
            self.bootstrap.handle_client,
            "127.0.0.1",
            0
        )

        self.bootstrap_port = (
            self.server.sockets[0].getsockname()[1]
        )

        self.bootstrap.port = self.bootstrap_port

    async def asyncTearDown(self):
        self.server.close()
        await self.server.wait_closed()

    def create_node(self, port):
        return PeerDiscovery(
            host="127.0.0.1",
            port=port,
            bootstrap_host="127.0.0.1",
            bootstrap_port=self.bootstrap_port
        )

    async def test_first_node_joins(self):
        node = self.create_node(9301)

        peers = await node.discover()

        self.assertEqual(len(peers), 1)
        self.assertEqual(
            peers[0].node_id,
            self.bootstrap.node_id
        )

    async def test_multiple_nodes_discover_each_other(self):
        node1 = self.create_node(9302)
        node2 = self.create_node(9303)

        await node1.discover()
        peers = await node2.discover()

        discovered_ids = [
            peer.node_id for peer in peers
        ]

        self.assertIn(node1.node_id, discovered_ids)
        self.assertIn(
            self.bootstrap.node_id,
            discovered_ids
        )

    async def test_routing_table_registration(self):
        node = self.create_node(9304)

        await node.discover()

        self.assertEqual(
            node.routing_table.get_statistics()["total_peers"],
            1
        )

    async def test_discovered_peer_storage(self):
        node = self.create_node(9305)

        await node.discover()

        self.assertEqual(
            len(node.get_discovered_peers()),
            1
        )


if __name__ == "__main__":
    unittest.main(verbosity=2)
