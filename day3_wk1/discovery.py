# discovery.py
import asyncio, json, logging

class Discovery(asyncio.DatagramProtocol):
    def __init__(self, node_id, tcp_port, table, on_event, discovery_port):
        self.node_id, self.tcp_port = node_id, tcp_port
        self.table, self.on_event = table, on_event
        self.discovery_port = discovery_port

    def connection_made(self, transport):
        self.transport = transport

    def datagram_received(self, data, addr):
        try:
            msg = json.loads(data.decode())
            if msg["type"] != "ANNOUNCE" or msg["node_id"] == self.node_id:
                return
            event = self.table.update(msg["node_id"], addr[0], msg["tcp_port"])
            if event:
                self.on_event(event, msg["node_id"])
        except (ValueError, KeyError):
            logging.warning("Invalid discovery packet from %s", addr)  # Day 1 validation idea

    async def beacon_loop(self, seed_ports, interval=2.0):
        payload = json.dumps({"type": "ANNOUNCE", "node_id": self.node_id,
                              "tcp_port": self.tcp_port}).encode()
        while True:
            for port in seed_ports:
                if port != self.discovery_port:
                    self.transport.sendto(payload, ("127.0.0.1", port))
            await asyncio.sleep(interval)
