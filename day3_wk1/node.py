import asyncio
import logging
import uuid

from peer_table import PeerTable
from discovery import Discovery
from task_queue import TaskQueue
from framing import read_msg, write_msg  # rename to match your Day 2 helpers

SEED_PORTS = [50001, 50002, 50003]


async def handle_client(reader, writer, table, queue):
    try:
        while True:
            req = await read_msg(reader)
            if req is None:               # client disconnected
                break
            await write_msg(writer, await handle_request(req, table, queue))
    except (asyncio.IncompleteReadError, ConnectionError):
        pass
    finally:
        writer.close()


async def handle_request(req, table, queue):
    kind = req.get("type")
    if kind == "PEERS":
        return {"type": "PEERS_RESPONSE",
                "peers": [vars(p) for p in table.peers.values()]}
    if kind == "SUBMIT_TASK":
        tid = await queue.add(req.get("payload", {}))
        return {"type": "TASK_ACCEPTED", "task_id": tid}
    if kind == "GET_TASK":
        t = await queue.get(req.get("worker_id", "anon"), timeout=2.0)
        return ({"type": "TASK", "task_id": t.task_id, "payload": t.payload}
                if t else {"type": "NO_TASK"})
    if kind == "COMPLETE_TASK":
        ok = await queue.complete(req.get("task_id"), req.get("result"))
        return ({"type": "TASK_DONE"} if ok
                else {"type": "ERROR", "reason": "unknown or not running"})
    if kind == "QUEUE_STATUS":
        return {"type": "QUEUE_STATUS_RESPONSE", **queue.stats()}
    return {"type": "ERROR", "reason": f"unsupported request: {kind}"}


async def reaper_loop(table, queue, interval=1.0):
    while True:
        for node_id, old, new in table.sweep():
            logging.info("Peer %s: %s -> %s", node_id[:8], old, new)
            if new == "DEAD":
                await queue.requeue_from(node_id)   # optional extra
        await asyncio.sleep(interval)


async def main():
    logging.basicConfig(level=logging.INFO,
                        format="%(asctime)s %(message)s")

    node_id = input("Enter Node ID (blank = auto): ").strip() or uuid.uuid4().hex
    tcp_port = int(input("Enter TCP port: "))
    discovery_port = 50000 + tcp_port % 1000

    table, queue = PeerTable(), TaskQueue()

    discovery = Discovery(
        node_id, tcp_port, table,
        lambda event, peer: logging.info("%s: %s", event, peer[:8]),
        discovery_port,
    )

    transport, _ = await asyncio.get_running_loop().create_datagram_endpoint(
        lambda: discovery, local_addr=("127.0.0.1", discovery_port)
    )

    server = await asyncio.start_server(
        lambda r, w: handle_client(r, w, table, queue),
        "127.0.0.1", tcp_port,
    )
    logging.info("Node %s up: TCP %d, UDP %d", node_id[:8], tcp_port, discovery_port)

    try:
        async with server:
            await asyncio.gather(
                discovery.beacon_loop(SEED_PORTS),
                reaper_loop(table, queue),
                server.serve_forever(),
            )
    finally:
        transport.close()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass