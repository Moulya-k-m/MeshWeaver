
import asyncio
import logging
import time

from framing import read_msg, write_msg
from security import sign, verify


class ResourceGossip:
    """
    Distributed resource monitoring and gossip engine.

    Day 12:
        - Validate resource reports.
        - Maintain resource state for peers.
        - Reject invalid, stale and older reports.

    Day 13:
        - Periodically exchange resource reports.
        - Run asynchronously in the background.
        - Handle peer communication failures.
    """

    def __init__(
        self,
        node_id,
        peer_table,
        scheduler,
        snapshot_function,
        interval=5.0,
        max_report_age=30.0,
    ):
        self.node_id = node_id
        self.peer_table = peer_table
        self.scheduler = scheduler
        self.snapshot_function = snapshot_function
        self.interval = interval
        self.max_report_age = max_report_age

        self.resource_state = {}
        self.last_update = {}

    # ==================================================
    # DAY 12 - RESOURCE STATE MANAGEMENT
    # ==================================================

    def create_report(self):
        """Create the current node's resource report."""

        return {
            "type": "LOAD_REPORT",
            "node_id": self.node_id,
            "timestamp": time.time(),
            "snapshot": self.snapshot_function(),
        }

    def validate_report(self, message):
        """Validate an incoming resource report."""

        if not isinstance(message, dict):
            return False

        if message.get("type") != "LOAD_REPORT":
            return False

        node_id = message.get("node_id")
        snapshot = message.get("snapshot")

        if not isinstance(node_id, str) or not node_id:
            return False

        # Reject our own report.
        if node_id == self.node_id:
            return False

        if not isinstance(snapshot, dict):
            return False

        required_fields = (
            "cpu",
            "ram",
            "active_tasks",
        )

        if not all(field in snapshot for field in required_fields):
            return False

        try:
            cpu = float(snapshot["cpu"])
            ram = float(snapshot["ram"])
            active_tasks = int(snapshot["active_tasks"])
            timestamp = float(message["timestamp"])

            if not 0 <= cpu <= 100:
                return False

            if not 0 <= ram <= 100:
                return False

            if active_tasks < 0:
                return False

            if timestamp <= 0:
                return False

            current_time = time.time()

            # Reject stale reports.
            if current_time - timestamp > self.max_report_age:
                logging.warning(
                    "Rejected stale resource report from %s",
                    node_id,
                )
                return False

            # Reject reports with timestamps too far in the future.
            if timestamp > current_time + 5:
                logging.warning(
                    "Rejected future resource report from %s",
                    node_id,
                )
                return False

        except (KeyError, TypeError, ValueError, OverflowError):
            return False

        return True

    def receive_report(self, message):
        """Accept and store a valid, newer resource report."""

        if not self.validate_report(message):
            logging.warning("Invalid resource report rejected")
            return False

        node_id = message["node_id"]
        snapshot = message["snapshot"]
        timestamp = float(message["timestamp"])

        previous_timestamp = self.last_update.get(node_id, 0)

        # Prevent older reports from overwriting newer information.
        if timestamp <= previous_timestamp:
            logging.debug(
                "Older report from %s ignored",
                node_id,
            )
            return False

        clean_snapshot = {
            "cpu": float(snapshot["cpu"]),
            "ram": float(snapshot["ram"]),
            "active_tasks": int(snapshot["active_tasks"]),
            "timestamp": timestamp,
        }

        self.resource_state[node_id] = clean_snapshot
        self.last_update[node_id] = timestamp

        # Update the existing scheduler.
        self.scheduler.update_load(
            node_id,
            clean_snapshot,
        )

        logging.info(
            "LOAD UPDATED | Node: %s | CPU: %.1f%% | RAM: %.1f%% | Tasks: %d",
            node_id[:8],
            clean_snapshot["cpu"],
            clean_snapshot["ram"],
            clean_snapshot["active_tasks"],
        )

        return True

    def get_peer_load(self, node_id):
        """Get the most recently received load report for a peer."""

        return self.resource_state.get(node_id)

    def get_all_resource_states(self):
        """Return all known peer resource information."""

        return dict(self.resource_state)

    def get_least_loaded_peer(self):
        """Return the peer with the lowest resource load score."""

        if not self.resource_state:
            return None

        def score(state):
            return (
                state["active_tasks"] * 20
                + state["cpu"] * 0.5
                + state["ram"] * 0.3
            )

        return min(
            self.resource_state.items(),
            key=lambda item: score(item[1]),
        )

    # ==================================================
    # DAY 13 - ASYNC GOSSIP ENGINE
    # ==================================================

    async def gossip_once(self, send_report):
        """Exchange resource reports with alive peers once."""

        peers = self.peer_table.alive_peers()

        if not peers:
            logging.debug("No alive peers available for gossip")
            return

        report = self.create_report()

        await asyncio.gather(
            *[
                self.exchange_with_peer(
                    peer,
                    report,
                    send_report,
                )
                for peer in peers
            ],
            return_exceptions=True,
        )

    async def exchange_with_peer(
        self,
        peer,
        report,
        send_report,
    ):
        """Send a report to an individual peer."""

        try:
            response = await asyncio.wait_for(
                send_report(peer, report),
                timeout=5.0,
            )

            if not isinstance(response, dict):
                logging.warning(
                    "Invalid response from peer %s",
                    peer.node_id[:8],
                )
                return

            response_type = response.get("type")

            if response_type == "LOAD_REPORT_ACK":
                logging.debug(
                    "Gossip ACK received from %s",
                    peer.node_id[:8],
                )

            elif response_type == "LOAD_REJECTED":
                logging.warning(
                    "Peer %s rejected resource report",
                    peer.node_id[:8],
                )

            else:
                logging.warning(
                    "Unexpected gossip response from %s: %s",
                    peer.node_id[:8],
                    response_type,
                )

        except asyncio.TimeoutError:
            logging.warning(
                "Gossip timeout with peer %s",
                peer.node_id[:8],
            )

        except Exception as exc:
            logging.warning(
                "Gossip communication failed with %s: %s",
                peer.node_id[:8],
                exc,
            )

    async def gossip_loop(self, send_report):
        """
        Run continuously until the Node cancels this task.

        IMPORTANT:
        This loop intentionally does not depend on self.running.
        The Node already manages it using asyncio task cancellation.
        """

        logging.info(
            "Resource gossip started for node %s",
            self.node_id[:8],
        )

        try:
            while True:
                start_time = time.monotonic()

                await self.gossip_once(send_report)

                elapsed = time.monotonic() - start_time
                remaining = max(0, self.interval - elapsed)

                await asyncio.sleep(remaining)

        except asyncio.CancelledError:
            logging.info(
                "Resource gossip stopped for node %s",
                self.node_id[:8],
            )
            raise

    # ==================================================
    # RESOURCE STATE CLEANUP
    # ==================================================

    def remove_peer(self, node_id):
        """Remove resource information for a dead peer."""

        self.resource_state.pop(node_id, None)
        self.last_update.pop(node_id, None)

        logging.info(
            "Removed resource state for peer %s",
            node_id[:8],
        )


# ======================================================
# NETWORK COMMUNICATION
# ======================================================

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
        signed_report = sign(report)

        await asyncio.wait_for(
            write_msg(writer, signed_report),
            timeout=3.0,
        )

        response = await asyncio.wait_for(
            read_msg(reader),
            timeout=3.0,
        )

        if not verify(response):
            raise ValueError(
                f"Invalid HMAC signature from peer {peer.node_id}"
            )

        return response

    finally:
        writer.close()

        try:
            await writer.wait_closed()

        except (ConnectionError, OSError):
            pass
