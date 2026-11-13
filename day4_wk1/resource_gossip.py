
import asyncio
import logging
from day3_wk1.framing import read_msg, write_msg


class ResourceGossip:
    def __init__(self, node_id, peer_table, scheduler,
                 snapshot_function, interval=5.0):
        self.node_id = node_id
        self.peer_table = peer_table
        self.scheduler = scheduler
        self.snapshot_function = snapshot_function
        self.interval = interval

    def create_report(self):
        return {
            "type": "LOAD_REPORT",
            "node_id": self.node_id,
            "snapshot": self.snapshot_function()
        }

    def receive_report(self, message):
        node_id = message.get("node_id")
        snapshot = message.get("snapshot")

        if not isinstance(node_id, str) or not node_id:
            return False

        if node_id == self.node_id or not isinstance(snapshot, dict):
            return False

        try:
            cpu = float(snapshot["cpu"])
            ram = float(snapshot["ram"])
            active = int(snapshot["active_tasks"])

            if not (0 <= cpu <= 100 and 0 <= ram <= 100):
                return False

            if active < 0:
                return False

            self.scheduler.update_load(node_id, {
                "cpu": cpu,
                "ram": ram,
                "active_tasks": active
            })
            return True

        except (KeyError, TypeError, ValueError):
            return False

    async def gossip_loop(self, send_report):
        while True:
            report = self.create_report()

            for node_id, peer in list(self.peer_table.peers.items()):
                if peer.state != "ALIVE":
                    continue

                try:
                    await send_report(peer, report)
                except (ConnectionError, OSError, asyncio.TimeoutError):
                    logging.warning(
                        "Could not send load report to %s", node_id[:8]
                    )

            await asyncio.sleep(self.interval)
    
async def send_load_report(peer, report):
    reader, writer = await asyncio.wait_for(
        asyncio.open_connection(peer.host, peer.tcp_port),
        timeout=3.0
    )

    try:
        await write_msg(writer, report)
        response = await asyncio.wait_for(read_msg(reader), timeout=3.0)
        return response
    finally:
        writer.close()
        await writer.wait_closed()


