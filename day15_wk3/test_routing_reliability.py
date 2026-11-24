import asyncio
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import AsyncMock

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "day5_wk1"))

from node import Node
from peer_table import PeerTable
from scheduler import Scheduler


class TestRoutingReliability(unittest.IsolatedAsyncioTestCase):

    async def test_scheduler_ignores_stale_load_report(self):
        peers = PeerTable()
        peer_id = "b" * 40

        peers.update(peer_id, "127.0.0.1", 18002)

        scheduler = Scheduler(peers, max_report_age=0.01)
        scheduler.update_load(
            peer_id,
            {"cpu": 0, "ram": 0, "active_tasks": 0},
        )

        await asyncio.sleep(0.03)

        self.assertIsNone(scheduler.choose_peer())
        print("PASS: Stale peer load reports are ignored")

    async def test_failed_forwarding_falls_back_to_local_queue(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            node = Node(
                "a" * 40,
                18001,
                journal_path=str(Path(temp_dir) / "tasks.jsonl"),
            )

            node.scheduler.choose_peer = lambda exclude=None: {
                "node_id": "b" * 40,
                "host": "127.0.0.1",
                "tcp_port": 18002,
                "load_score": -1,
            }

            node.request_peer = AsyncMock(
                side_effect=OSError("Simulated peer unavailable")
            )

            try:
                response = await node.handle_request({
                    "type": "SUBMIT_TASK",
                    "payload": {
                        "operation": "ECHO",
                        "value": "local fallback test",
                    },
                })

                self.assertEqual(response["type"], "TASK_ACCEPTED")
                self.assertFalse(response["forwarded"])
                self.assertEqual(response["node_id"], node.node_id)
                self.assertIsNotNone(node.store.get(response["task_id"]))

                print("PASS: Failed forwarding falls back to local queue")

            finally:
                node.store.close()


if __name__ == "__main__":
    unittest.main()
