
import argparse
import asyncio
from csv import reader, writer
from email import message
import logging
import time
import uuid

from day3_wk1.peer_table import PeerTable
from day3_wk1.discovery import Discovery
from day3_wk1.framing import read_msg, write_msg

from day4_wk1.task_store import TaskStore
from day4_wk1.scheduler import Scheduler
from day4_wk1.resource_monitor import snapshot,load_score
from day4_wk1.resource_gossip import (
    ResourceGossip,
    send_load_report,
)
from day4_wk1.worker import worker_loop


SEED_PORTS = [50001, 50002, 50003]


class Node:

    def __init__(self, node_id, tcp_port):

        self.node_id = node_id
        self.tcp_port = tcp_port
        self.udp_port = 50000 + tcp_port % 1000

        self.started = time.monotonic()

        # Peer management
        self.table = PeerTable()

        # Task management
        self.store = TaskStore(node_id)
        # Track tasks forwarded to other nodes
        self.remote_tasks = {}

        # Load-based scheduler
        self.scheduler = Scheduler(self.table)

        # Resource gossip
        self.gossip = ResourceGossip(
            node_id=node_id,
            peer_table=self.table,
            scheduler=self.scheduler,
            snapshot_function=lambda: snapshot(
                self.store.active_count()
            ),
            interval=5.0,
        )

        # UDP discovery
        self.discovery = Discovery(
            node_id,
            tcp_port,
            self.table,
            self.on_peer_event,
            self.udp_port,
        )

    def on_peer_event(self, event, peer_id):
        logging.info(
            "Peer event: %s - %s",
            event,
            peer_id[:8],
        )

    def current_load(self):
        return snapshot(self.store.active_count())

    async def request_peer(self, host, port, message):
        reader, writer = await asyncio.wait_for(
        asyncio.open_connection(host, port),
        timeout=3.0,
    )

        try:
            await write_msg(writer, message)

            return await asyncio.wait_for(
                 read_msg(reader),
                 timeout=3.0,
        )

        finally:
            writer.close()
            await writer.wait_closed()

    async def handle_request(self, req):

        kind = req.get("type") if isinstance(req, dict) else None

        # Peer discovery information
        if kind == "PEERS":
            return {
                "type": "PEERS_RESPONSE",
                "peers": [
                    vars(peer)
                    for peer in self.table.peers.values()
                ],
            }

        # Node health and resource information
        if kind == "STATUS":
            return {
                "type": "STATUS_RESPONSE",
                "node_id": self.node_id,
                "uptime_seconds": round(
                    time.monotonic() - self.started, 2
                ),
                "load": self.current_load(),
                "queue": self.store.stats(),
                "peer_count": len(self.table.peers),
            }

        # Exchange resource information
        if kind == "LOAD_REPORT":

            sender = req.get("node_id")
            peer = self.table.peers.get(sender)

            if peer is None or peer.state != "ALIVE":
                return {
                    "type": "LOAD_REJECTED",
                    "reason": "Unknown or inactive peer",
                }

            accepted = self.gossip.receive_report(req)

            if accepted:
                logging.info(
                    "Received resource report from peer %s",
                    sender[:8],
                )

            return {
                "type": "LOAD_ACK" if accepted else "LOAD_REJECTED"
            }

        # Submit a task locally
        if kind == "SUBMIT_TASK":

            payload = req.get("payload")

            if not isinstance(payload, dict):
                return {
                    "type": "ERROR",
                    "reason": "Payload must be a dictionary",
                }

            # Compare our load with the least-loaded peer
            local_score = load_score(self.current_load())

            peer = self.scheduler.choose_peer(
                exclude=self.node_id
            )

            # Forward only if a peer has a lower load
            if peer and peer["load_score"] < local_score:

                task_id = uuid.uuid4().hex[:8]

                try:
                    response = await self.request_peer(
                        peer["host"],
                        peer["tcp_port"],
                        {
                            "type": "FORWARD_TASK",
                            "task_id": task_id,
                            "payload": payload,
                            "origin": self.node_id,
                            "hops": 1,
                        },
                    )

                    if response.get("type") == "TASK_ACCEPTED":
                        self.remote_tasks[task_id] = {
                            "host": peer["host"],
                            "tcp_port": peer["tcp_port"],
                            "node_id": peer["node_id"],
                        }

                        logging.info(
                            "Task %s forwarded to peer %s",
                            task_id,
                            peer["node_id"][:8],
                        )

                        return {
                            "type": "TASK_ACCEPTED",
                            "task_id": task_id,
                            "node_id": peer["node_id"],
                            "forwarded": True,
                        }

                except (ConnectionError, OSError, asyncio.TimeoutError):
                    logging.warning(
                        "Could not forward task to peer %s",
                        peer["node_id"][:8],
                    )

            # No suitable peer: execute locally
            task_id = await self.store.add(
                payload,
                origin=self.node_id,
            )

            return {
                "type": "TASK_ACCEPTED",
                "task_id": task_id,
                "node_id": self.node_id,
                "forwarded": False,
            }

        # Receive a task forwarded by another node
        if kind == "FORWARD_TASK":

            payload = req.get("payload")
            task_id = req.get("task_id")
            hops = req.get("hops", 1)

            if (
                not isinstance(payload, dict)
                or not isinstance(task_id, str)
                or not isinstance(hops, int)
                or isinstance(hops, bool)
                or hops < 0
                or hops > 1
            ):
                return {
                    "type": "ERROR",
                    "reason": "Invalid forwarded task",
                }

            await self.store.add(
                payload,
                task_id=task_id,
                hops=hops,
                origin=req.get("origin"),
            )

            return {
                "type": "TASK_ACCEPTED",
                "task_id": task_id,
                "node_id": self.node_id,
            }

        # Retrieve a task result
        if kind == "GET_RESULT":

            task_id = req.get("task_id")

            # Check whether this task was forwarded
            remote = self.remote_tasks.get(task_id)

            if remote:

                try:
                    return await self.request_peer(
                        remote["host"],
                        remote["tcp_port"],
                        {
                            "type": "GET_RESULT",
                            "task_id": task_id,
                        },
                    )

                except (ConnectionError, OSError, asyncio.TimeoutError):
                    return {
                        "type": "RESULT_UNAVAILABLE",
                        "task_id": task_id,
                        "reason": "Remote node is unavailable",
                    }

            # Otherwise retrieve the local result
            task = self.store.get(task_id)

            if task is None:
                return {
                    "type": "RESULT_NOT_FOUND",
                    "task_id": task_id,
                }

            return {
                "type": "RESULT_RESPONSE",
                "task_id": task.task_id,
                "status": task.status,
                "result": task.result,
                "error": task.error,
            }
        # Basic connection test
        if kind == "HELLO":
            return {
                "type": "HELLO_ACK",
                "node_id": self.node_id,
            }

        return {
            "type": "ERROR",
            "reason": f"Unsupported request: {kind}",
        }

    async def handle_client(self, reader, writer):

        try:
            while True:
                req = await read_msg(reader)
                response = await self.handle_request(req)
                await write_msg(writer, response)

        except asyncio.IncompleteReadError:
            pass

        except (ConnectionError, OSError):
            pass

        except Exception:
            logging.exception("Client request failed")

        finally:
            writer.close()

            try:
                await writer.wait_closed()
            except ConnectionError:
                pass

    async def reaper_loop(self):

        while True:

            changes = self.table.sweep()

            for node_id, old, new in changes:

                logging.info(
                    "Peer %s: %s -> %s",
                    node_id[:8],
                    old,
                    new,
                )

                if new == "DEAD":
                    self.scheduler.load_reports.pop(
                        node_id, None
                    )

            await asyncio.sleep(1.0)

    async def run(self):

        loop = asyncio.get_running_loop()

        # Start UDP discovery
        transport, _ = await loop.create_datagram_endpoint(
            lambda: self.discovery,
            local_addr=("127.0.0.1", self.udp_port),
        )

        # Start TCP server
        server = await asyncio.start_server(
            self.handle_client,
            "127.0.0.1",
            self.tcp_port,
        )

        logging.info(
            "Node %s started | TCP: %d | UDP: %d",
            self.node_id[:8],
            self.tcp_port,
            self.udp_port,
        )

        # Background operations
        gossip_task = asyncio.create_task(
            self.gossip.gossip_loop(send_load_report)
        )

        discovery_task = asyncio.create_task(
            self.discovery.beacon_loop(SEED_PORTS)
        )

        reaper_task = asyncio.create_task(
            self.reaper_loop()
        )

        # Start worker
        worker_task = asyncio.create_task(
            worker_loop(self.store, self.node_id)
        )

        try:
            async with server:
                await server.serve_forever()

        finally:

            # Cancel all background tasks
            for task in (
                gossip_task,
                discovery_task,
                reaper_task,
                worker_task,
            ):
                task.cancel()

            await asyncio.gather(
                gossip_task,
                discovery_task,
                reaper_task,
                worker_task,
                return_exceptions=True,
            )

            server.close()
            await server.wait_closed()
            transport.close()

            logging.info(
                "Node %s stopped",
                self.node_id[:8],
            )


async def main():

    parser = argparse.ArgumentParser(
        description="MeshWeaver Day 4 Node"
    )

    parser.add_argument(
        "--tcp",
        type=int,
        required=True,
        help="TCP port: 8001, 8002 or 8003",
    )

    parser.add_argument(
        "--id",
        default=None,
        help="Optional node ID",
    )

    args = parser.parse_args()

    node_id = args.id or uuid.uuid4().hex

    node = Node(node_id, args.tcp)

    await node.run()


if __name__ == "__main__":

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(message)s",
    )

    try:
        asyncio.run(main())

    except KeyboardInterrupt:
        print("\nMeshWeaver node stopped.")
