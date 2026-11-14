
import asyncio
import json
import logging

from security import sign, verify


class Discovery(asyncio.DatagramProtocol):

    def __init__(
        self,
        node_id,
        tcp_port,
        table,
        on_event,
        discovery_port
    ):
        self.node_id = node_id
        self.tcp_port = tcp_port
        self.table = table
        self.on_event = on_event
        self.discovery_port = discovery_port

    def connection_made(self, transport):
        self.transport = transport

    def datagram_received(self, data, addr):

        try:
            msg = json.loads(data.decode())

            if not verify(msg):
                logging.warning(
                    "Rejected invalid beacon from %s", addr
                )
                return

            if msg.get("type") != "ANNOUNCE":
                return

            sender_id = msg.get("node_id")
            sender_port = msg.get("tcp_port")

            if not isinstance(sender_id, str):
                return

            if not isinstance(sender_port, int) or not 1 <= sender_port <= 65535:
                return

            if sender_id == self.node_id:
                return

            # The sender is directly reachable.
            event = self.table.update(
                sender_id,
                addr[0],
                sender_port
            )

            if event:
                self.on_event(event, sender_id)

            # Learn about the sender's known peers.
            known_peers = msg.get("peers", [])

            if not isinstance(known_peers, list):
                return

            for peer in known_peers[:50]:

                if not isinstance(peer, dict):
                    continue

                peer_id = peer.get("node_id")
                peer_host = peer.get("host")
                peer_port = peer.get("tcp_port")

                if not isinstance(peer_id, str):
                    continue

                if peer_id == self.node_id or peer_id == sender_id:
                    continue

                if not isinstance(peer_host, str):
                    continue

                if not isinstance(peer_port, int) or not 1 <= peer_port <= 65535:
                    continue

                learned = self.table.learn_indirect(
                    peer_id,
                    peer_host,
                    peer_port
                )

                if learned:
                    logging.info(
                        "Learned peer %s indirectly through %s",
                        peer_id,
                        sender_id
                    )

        except (ValueError, KeyError, TypeError):
            logging.warning(
                "Invalid discovery packet from %s", addr
            )

    async def beacon_loop(self, seed_ports, interval=2.0):

        while True:

            payload = {
                "type": "ANNOUNCE",
                "node_id": self.node_id,
                "tcp_port": self.tcp_port,

                # Share known peer information.
                "peers": self.table.gossip_peers()
            }

            signed_payload = json.dumps(
                sign(payload)
            ).encode()

            for port in seed_ports:

                if port != self.discovery_port:
                    self.transport.sendto(
                        signed_payload,
                        ("127.0.0.1", port)
                    )

            await asyncio.sleep(interval)
