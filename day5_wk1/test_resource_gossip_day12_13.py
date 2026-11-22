import asyncio
import time
import unittest

from resource_gossip import ResourceGossip
from scheduler import Scheduler


class FakePeer:
    def __init__(self, node_id):
        self.node_id = node_id
        self.host = "127.0.0.1"
        self.tcp_port = 9001
        self.state = "ALIVE"


class FakePeerTable:
    def __init__(self):
        self.peers = {
            "NODE_B": FakePeer("NODE_B")
        }

    def alive_peers(self):
        return [
            peer for peer in self.peers.values()
            if peer.state == "ALIVE"
        ]


class ResourceGossipTests(unittest.TestCase):

    def setUp(self):
        self.peer_table = FakePeerTable()
        self.scheduler = Scheduler(self.peer_table)

        self.gossip = ResourceGossip(
            node_id="NODE_A",
            peer_table=self.peer_table,
            scheduler=self.scheduler,
            snapshot_function=lambda: {
                "cpu": 20.0,
                "ram": 40.0,
                "active_tasks": 2
            },
            interval=0.01
        )

    def make_report(self, timestamp=None):
        return {
            "type": "LOAD_REPORT",
            "node_id": "NODE_B",
            "timestamp": timestamp or time.time(),
            "snapshot": {
                "cpu": 35.0,
                "ram": 50.0,
                "active_tasks": 3
            }
        }

    def test_valid_report_updates_resource_state(self):
        report = self.make_report()

        result = self.gossip.receive_report(report)

        self.assertTrue(result)
        self.assertIn("NODE_B", self.gossip.resource_state)
        self.assertIn("NODE_B", self.scheduler.load_reports)

    def test_invalid_report_is_rejected(self):
        report = self.make_report()
        report["snapshot"]["cpu"] = 150

        self.assertFalse(self.gossip.receive_report(report))

    def test_own_report_is_rejected(self):
        report = self.make_report()
        report["node_id"] = "NODE_A"

        self.assertFalse(self.gossip.receive_report(report))

    def test_stale_report_is_rejected(self):
        report = self.make_report(time.time() - 100)

        self.assertFalse(self.gossip.receive_report(report))

    def test_older_report_does_not_replace_newer_report(self):
        first = self.make_report(time.time())
        self.assertTrue(self.gossip.receive_report(first))

        older = self.make_report(first["timestamp"] - 1)
        self.assertFalse(self.gossip.receive_report(older))


class AsyncResourceGossipTests(unittest.IsolatedAsyncioTestCase):

    async def test_gossip_once_sends_report_to_alive_peer(self):
        peer_table = FakePeerTable()
        scheduler = Scheduler(peer_table)

        gossip = ResourceGossip(
            node_id="NODE_A",
            peer_table=peer_table,
            scheduler=scheduler,
            snapshot_function=lambda: {
                "cpu": 10.0,
                "ram": 25.0,
                "active_tasks": 1
            }
        )

        sent_to = []

        async def fake_send(peer, report):
            sent_to.append(peer.node_id)
            return {"type": "LOAD_REPORT_ACK"}

        await gossip.gossip_once(fake_send)

        self.assertEqual(sent_to, ["NODE_B"])

    async def test_gossip_loop_stops_when_cancelled(self):
        peer_table = FakePeerTable()
        scheduler = Scheduler(peer_table)

        gossip = ResourceGossip(
            node_id="NODE_A",
            peer_table=peer_table,
            scheduler=scheduler,
            snapshot_function=lambda: {
                "cpu": 10.0,
                "ram": 25.0,
                "active_tasks": 1
            },
            interval=0.01
        )

        async def fake_send(peer, report):
            return {"type": "LOAD_REPORT_ACK"}

        task = asyncio.create_task(
            gossip.gossip_loop(fake_send)
        )

        await asyncio.sleep(0.03)
        task.cancel()

        with self.assertRaises(asyncio.CancelledError):
            await task


if __name__ == "__main__":
    unittest.main()
