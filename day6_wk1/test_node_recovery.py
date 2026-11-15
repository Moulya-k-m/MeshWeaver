
import asyncio
import tempfile
import sys
from pathlib import Path

DAY5_PATH = Path(__file__).resolve().parents[1] / "day5_wk1"
sys.path.insert(0, str(DAY5_PATH))

from node import Node


def test_node_restores_tasks_after_restart():

    async def scenario():

        with tempfile.TemporaryDirectory() as temp:

            journal_path = str(Path(temp) / "node_tasks.jsonl")

            node1 = Node("NODE1", 8001, journal_path)

            await node1.store.add(
                {"operation": "test"},
                task_id="T301"
            )

            await node1.store.claim("WORKER1")

            node1.store.close()

            node2 = Node("NODE1", 8001, journal_path)

            try:
                task = node2.store.get("T301")

                assert task is not None
                assert task.status == "PENDING"
                assert task.assigned_to is None
                assert node2.store.recovered == 1

            finally:
                node2.store.close()

    asyncio.run(scenario())
