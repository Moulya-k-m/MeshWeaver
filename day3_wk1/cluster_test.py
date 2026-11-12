# cluster_test.py
import asyncio
from framing import read_msg, write_msg   # same names as in node.py

HOST, PORT = "127.0.0.1", 5001     # node 1


async def request(req, port=PORT):
    reader, writer = await asyncio.open_connection(HOST, port)
    await write_msg(writer, req)
    resp = await read_msg(reader)
    writer.close()
    await writer.wait_closed()
    return resp


def check(name, condition):
    print(f"{'PASS' if condition else 'FAIL'}  {name}")
    return condition


async def main():
    results = []

    # Test 1: peer discovery
    resp = await request({"type": "PEERS"})
    peers = resp["peers"]
    results.append(check("PEERS returns 2 peers", len(peers) == 2))
    results.append(check("All peers ALIVE", all(p["state"] == "ALIVE" for p in peers)))

    # Test 2: submit 3 tasks
    ids = []
    for name in ["A", "B", "C"]:
        r = await request({"type": "SUBMIT_TASK", "payload": {"name": name}})
        ids.append(r["task_id"])
    results.append(check("3 tasks accepted", len(ids) == 3))

    r = await request({"type": "QUEUE_STATUS"})
    results.append(check("PENDING == 3", r["PENDING"] == 3))

    # Test 3: FIFO order
    got = []
    for _ in range(3):
        r = await request({"type": "GET_TASK", "worker_id": "tester"})
        got.append(r.get("payload", {}).get("name"))
    results.append(check("FIFO order A, B, C", got == ["A", "B", "C"]))

    r = await request({"type": "GET_TASK", "worker_id": "tester"})
    results.append(check("Empty queue returns NO_TASK", r["type"] == "NO_TASK"))

    # Test 4: complete a task
    r = await request({"type": "COMPLETE_TASK", "task_id": ids[0], "result": "ok"})
    results.append(check("Complete task A", r["type"] == "TASK_DONE"))

    r = await request({"type": "COMPLETE_TASK", "task_id": ids[0]})
    results.append(check("Completing A twice returns ERROR", r["type"] == "ERROR"))

    r = await request({"type": "QUEUE_STATUS"})
    results.append(check("DONE == 1, RUNNING == 2", r["DONE"] == 1 and r["RUNNING"] == 2))

    # Test 5: bad requests don't crash the node
    r = await request({"type": "NONSENSE"})
    results.append(check("Unknown request returns ERROR", r["type"] == "ERROR"))
    r = await request({"type": "COMPLETE_TASK", "task_id": "doesnotexist"})
    results.append(check("Unknown task ID returns ERROR", r["type"] == "ERROR"))

    print(f"\n{sum(results)}/{len(results)} checks passed")


if __name__ == "__main__":
    asyncio.run(main())