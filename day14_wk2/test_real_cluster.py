
import asyncio
import sys
import tempfile
import unittest
import uuid

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "day5_wk1"))

from day5_wk1.node import Node


async def wait_until(condition, timeout=15):
    """Wait until a cluster condition becomes true."""

    deadline = asyncio.get_running_loop().time() + timeout

    while asyncio.get_running_loop().time() < deadline:
        if condition():
            return True

        await asyncio.sleep(0.2)

    return False


class TestRealCluster(unittest.IsolatedAsyncioTestCase):

    async def test_three_node_gossip_and_failure_detection(self):

        with tempfile.TemporaryDirectory() as temp_dir:

            ports = [18001, 18002, 18003]

            nodes = [
                Node(
                    uuid.uuid4().hex,
                    port,
                    journal_path=str(
                        Path(temp_dir) / f"node_{port}.jsonl"
                    ),
                )
                for port in ports
            ]

            # Shorter failure timeout for this integration test.
            for node in nodes:
                node.table.suspect_after = 2.0
                node.table.dead_after = 4.0

            tasks = [
                asyncio.create_task(node.run())
                for node in nodes
            ]

            try:
                # Wait for all three nodes to discover each other.
                discovered = await wait_until(
                    lambda: all(
                        len(node.table.alive_peers()) == 2
                        for node in nodes
                    ),
                    timeout=12,
                )

                self.assertTrue(
                    discovered,
                    "All three nodes should discover each other",
                )

                # Wait for real signed resource reports.
                gossiped = await wait_until(
                    lambda: all(
                        all(
                            peer.node_id in node.gossip.resource_state
                            and peer.node_id in node.scheduler.load_reports
                            for peer in node.table.alive_peers()
                        )
                        for node in nodes
                    ),
                    timeout=15,
                )

                self.assertTrue(
                    gossiped,
                    "All nodes should exchange resource reports",
                )

                print("\nPASS: Three nodes discovered each other")
                print("PASS: Signed resource gossip exchanged")
                print("PASS: Scheduler received peer load reports")

                # Stop the third node.
                stopped_id = nodes[2].node_id

                tasks[2].cancel()
                await asyncio.gather(
                    tasks[2],
                    return_exceptions=True,
                )

                # Remaining nodes should eventually mark it DEAD.
                detected_failure = await wait_until(
                    lambda: all(
                        node.table.peers[stopped_id].state == "DEAD"
                        for node in nodes[:2]
                        if stopped_id in node.table.peers
                    )
                    and all(
                        stopped_id in node.table.peers
                        and node.table.peers[stopped_id].state == "DEAD"
                        for node in nodes[:2]
                    ),
                    timeout=8,
                )

                self.assertTrue(
                    detected_failure,
                    "Remaining nodes should detect the stopped peer",
                )

                # Verify resource information is cleaned up.
                for node in nodes[:2]:
                    self.assertNotIn(
                        stopped_id,
                        node.gossip.resource_state,
                    )
                    self.assertNotIn(
                        stopped_id,
                        node.scheduler.load_reports,
                    )

                print("PASS: Failed peer detected")
                print("PASS: Dead peer resource data cleaned up")

            finally:
                for task in tasks:
                    if not task.done():
                        task.cancel()

                await asyncio.gather(
                    *tasks,
                    return_exceptions=True,
                )


if __name__ == "__main__":
    unittest.main()

