
import asyncio
import logging

from framing import read_msg, write_msg
from security import sign, verify


class ResourceGossip:
    def __init__(
        self,
        node_id,
        peer_table,
        scheduler,
        snapshot_function,
        interval=5.0,
    ):
        self.node_id = node_id
        self.peer_table = peer_table
        self.scheduler = scheduler
        self.snapshot_function = snapshot_function
        self.interval = interval

    def create_report(self):
        """Create this node's resource report."""
        report = {
            "type": "LOAD_REPORT",
            "node_id": self.node_id,
            "snapshot": self.snapshot_function(),
        }

        return report

    def receive_report(self, message):
        """Validate and process a resource report."""

        node_id = message.get("node_id")
        snapshot = message.get("snapshot")

        if not node_id or not isinstance(snapshot, dict):
            logging.warning("Invalid resource report received")
            return False

        required_fields = ("cpu", "ram", "active_tasks")

        if not all(field in snapshot for field in required_fields):
            logging.warning(
                "Incomplete resource report from %s",
                node_id,
            )
            return False

        try:
            cpu = float(snapshot["cpu"])
            ram = float(snapshot["ram"])
            active_tasks = int(snapshot["active_tasks"])

            if not (0 <= cpu <= 100 and 0 <= ram <= 100):
                raise ValueError("CPU or RAM percentage out of range")

            if active_tasks < 0:
                raise ValueError("Negative active task count")

        except (TypeError, ValueError):
            logging.warning(
                "Invalid resource values from %s",
                node_id,
            )
            return False

        self.scheduler.update_load(
            node_id,
            {
                "cpu": cpu,
                "ram": ram,
                "active_tasks": active_tasks,
            },
        )

        logging.info(
            "Updated resource information for peer %s",
            node_id,
        )

        return True

    async def gossip_loop(self, send_report):
        """Periodically share resource information with alive peers."""

        while True:
            report = self.create_report()

            peers = self.peer_table.alive_peers()

            for peer in peers:
                try:
                    response = await send_report(peer, report)

                    if not isinstance(response, dict):
                        logging.warning(
                            "Invalid response from peer %s",
                            peer.node_id,
                        )
                        continue

                    if response.get("type") != "LOAD_REPORT_ACK":
                        logging.warning(
                            "Unexpected response from peer %s",
                            peer.node_id,
                        )

                except Exception as exc:
                    logging.warning(
                        "Gossip failed with peer %s: %s",
                        peer.node_id,
                        exc,
                    )

            await asyncio.sleep(self.interval)


async def send_load_report(peer, report):
    """Send a signed resource report and verify the response."""

    reader, writer = await asyncio.wait_for(
        asyncio.open_connection(
            peer.host,
            peer.tcp_port,
        ),
        timeout=3.0,
    )

    try:
        # Sign the outgoing report.
        signed_report = sign(report)

        await asyncio.wait_for(
            write_msg(writer, signed_report),
            timeout=3.0,
        )

        # Receive the peer's response.
        response = await asyncio.wait_for(
            read_msg(reader),
            timeout=3.0,
        )

        # Verify the received response.
        if not verify(response):
            raise ValueError(
                f"Invalid HMAC signature from peer {peer.node_id}"
            )

        return response

    finally:
        writer.close()
        await writer.wait_closed()
