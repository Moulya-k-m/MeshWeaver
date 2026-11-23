
import asyncio
import logging


class DiscoveryGossipIntegration:
    """
    Day 14: Integrate peer discovery with resource gossip.

    Responsibilities:
    - Discover peers using the existing PeerDiscovery module.
    - Register discovered peers in PeerTable.
    - Exclude the bootstrap server from resource gossip.
    - Start and stop the existing gossip loop.
    - Remove resource data when a peer becomes DEAD.
    """

    def __init__(
        self,
        discovery,
        peer_table,
        resource_gossip,
        send_report,
    ):
        self.discovery = discovery
        self.peer_table = peer_table
        self.resource_gossip = resource_gossip
        self.send_report = send_report

        self.gossip_task = None

    async def discover_and_register(self):
        """Discover peers and register them in PeerTable."""

        discovered = await self.discovery.discover()
        registered = []

        for peer in discovered:

            # The bootstrap server only handles JOIN requests.
            if (
                peer.ip == self.discovery.bootstrap_host
                and peer.port == self.discovery.bootstrap_port
            ):
                continue

            result = self.peer_table.update(
                node_id=peer.node_id,
                host=peer.ip,
                tcp_port=peer.port,
            )

            registered.append(peer.node_id)

            logging.info(
                "Peer registered: %s (%s:%s) [%s]",
                peer.node_id[:8],
                peer.ip,
                peer.port,
                result,
            )

        return registered

    async def start(self):
        """Discover peers and start background resource gossip."""

        if self.gossip_task and not self.gossip_task.done():
            return

        registered = await self.discover_and_register()

        logging.info(
            "Day 14 integration: registered %d peer(s)",
            len(registered),
        )

        self.gossip_task = asyncio.create_task(
            self.resource_gossip.gossip_loop(
                self.send_report
            )
        )

        logging.info("Discovery-gossip integration started")

    async def refresh_peers(self):
        """Discover and register peers again."""

        return await self.discover_and_register()

    def sweep_peers(self):
        """Check peer health and clean up dead peer resource data."""

        changes = self.peer_table.sweep()

        for node_id, old_state, new_state in changes:

            logging.info(
                "Peer state changed: %s | %s -> %s",
                node_id[:8],
                old_state,
                new_state,
            )

            if new_state == "DEAD":
                self.resource_gossip.remove_peer(node_id)

                # Also clear the scheduler's cached load report.
                self.resource_gossip.scheduler.load_reports.pop(
                    node_id,
                    None,
                )

        return changes

    async def stop(self):
        """Stop the background gossip task safely."""

        if self.gossip_task is None:
            return

        self.gossip_task.cancel()

        try:
            await self.gossip_task
        except asyncio.CancelledError:
            pass

        self.gossip_task = None

        logging.info("Discovery-gossip integration stopped")
