
import asyncio
import unittest

from day14_wk2.integration import DiscoveryGossipIntegration
from day5_wk1.peer_table import PeerTable
from day9_wk2.peer import Peer


class FakeDiscovery:

    bootstrap_host = "127.0.0.1"
    bootstrap_port = 9200

    async def discover(self):
        return [
            Peer(
                node_id="a" * 40,
                ip="127.0.0.1",
                port=9301,
            ),
            Peer(
                node_id="b" * 40,
                ip="127.0.0.1",
                port=9200,
            ),
        ]


class FakeGossip:

    def __init__(self):
        self.removed = []
        self.scheduler = type(
            "Scheduler",
            (),
            {"load_reports": {}},
        )()

    async def gossip_loop(self, send_report):
        await asyncio.Event().wait()

    def remove_peer(self, node_id):
        self.removed.append(node_id)


class TestDay14Integration(unittest.IsolatedAsyncioTestCase):

    async def test_discovery_registers_peers_and_skips_bootstrap(self):

        peer_table = PeerTable()

        integration = DiscoveryGossipIntegration(
            discovery=FakeDiscovery(),
            peer_table=peer_table,
            resource_gossip=FakeGossip(),
            send_report=None,
        )

        registered = await integration.discover_and_register()

        self.assertEqual(registered, ["a" * 40])
        self.assertIn("a" * 40, peer_table.peers)
        self.assertNotIn("b" * 40, peer_table.peers)

        peer = peer_table.peers["a" * 40]

        self.assertEqual(peer.host, "127.0.0.1")
        self.assertEqual(peer.tcp_port, 9301)
        self.assertEqual(peer.state, "ALIVE")

    async def test_dead_peer_resource_cleanup(self):

        peer_table = PeerTable(
            suspect_after=0,
            dead_after=0,
        )

        peer_table.update(
            "a" * 40,
            "127.0.0.1",
            9301,
        )

        gossip = FakeGossip()
        gossip.scheduler.load_reports["a" * 40] = {}

        integration = DiscoveryGossipIntegration(
            discovery=FakeDiscovery(),
            peer_table=peer_table,
            resource_gossip=gossip,
            send_report=None,
        )

        await asyncio.sleep(0.01)

        changes = integration.sweep_peers()

        self.assertEqual(len(changes), 1)
        self.assertEqual(changes[0][2], "DEAD")
        self.assertIn("a" * 40, gossip.removed)
        self.assertNotIn("a" * 40, gossip.scheduler.load_reports)


if __name__ == "__main__":
    unittest.main()
