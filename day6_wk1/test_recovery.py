
import asyncio
import tempfile
import sys
from pathlib import Path

DAY5_PATH = Path(__file__).resolve().parents[1] / "day5_wk1"
sys.path.insert(0, str(DAY5_PATH))

from task_store import TaskStore


def test_running_task_recovers_after_restart():

    async def scenario():

        with tempfile.TemporaryDirectory() as temp:
            journal_path = str(Path(temp) / "tasks.jsonl")

            store = TaskStore("NODE1", journal_path=journal_path)

            await store.add({"operation": "test"}, task_id="T101")
            await store.claim("WORKER1")

            assert store.get("T101").status == "RUNNING"

            store.close()

            restarted = TaskStore("NODE1", journal_path=journal_path)

            try:
                task = restarted.get("T101")

                assert task is not None
                assert task.status == "PENDING"
                assert task.assigned_to is None
                assert restarted.recovered == 1
                assert "T101" in restarted.pending
            finally:
                restarted.close()

    asyncio.run(scenario())


def test_completed_task_remains_completed():

    async def scenario():

        with tempfile.TemporaryDirectory() as temp:
            journal_path = str(Path(temp) / "tasks.jsonl")

            store = TaskStore("NODE1", journal_path=journal_path)

            await store.add({"operation": "test"}, task_id="T102")
            await store.claim("WORKER1")
            await store.complete("T102", "SUCCESS")

            store.close()

            restarted = TaskStore("NODE1", journal_path=journal_path)

            try:
                assert restarted.get("T102").status == "COMPLETED"
                assert restarted.recovered == 0
            finally:
                restarted.close()

    asyncio.run(scenario())


def test_multiple_tasks_recover_correctly():

    async def scenario():

        with tempfile.TemporaryDirectory() as temp:
            journal_path = str(Path(temp) / "tasks.jsonl")

            store = TaskStore("NODE1", journal_path=journal_path)

            await store.add({"job": "A"}, task_id="T201")
            await store.add({"job": "B"}, task_id="T202")
            await store.add({"job": "C"}, task_id="T203")

            await store.claim("WORKER1")
            await store.claim("WORKER2")
            await store.claim("WORKER3")

            await store.complete("T203", "DONE")

            store.close()

            restarted = TaskStore("NODE1", journal_path=journal_path)

            try:
                assert restarted.get("T201").status == "PENDING"
                assert restarted.get("T202").status == "PENDING"
                assert restarted.get("T203").status == "COMPLETED"

                assert restarted.recovered == 2
                assert len(restarted.pending) == 2
            finally:
                restarted.close()

    asyncio.run(scenario())
