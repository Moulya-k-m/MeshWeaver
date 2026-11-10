import argparse
import asyncio
import hashlib
import json
import logging
import uuid

log = logging.getLogger("listener")


class ListenerProtocol(asyncio.DatagramProtocol):
    def __init__(self, node_id: str):
        self.node_id = node_id
        self.transport = None
        self.handled = 0

    def connection_made(self, transport):
        self.transport = transport
        log.info("Node %s listening on %s", self.node_id[:8], transport.get_extra_info("sockname"))

    def datagram_received(self, data, addr):
        # Never trust incoming bytes: validate before using them.
        try:
            msg = json.loads(data.decode("utf-8"))
            if not isinstance(msg, dict) or msg.get("type") != "PING":
                raise ValueError("not a PING message")
            seq = msg["seq"]
        except (ValueError, KeyError) as exc:
            log.warning("Dropped bad packet from %s: %s", addr, exc)
            return

        self.handled += 1
        log.info("PING seq=%s from node %s at %s", seq, str(msg.get("node_id", "?"))[:8], addr)

        reply = {
            "type": "PONG",
            "seq": seq,
            "node_id": self.node_id,
            "echo_ts": msg.get("ts"),
        }
        self.transport.sendto(json.dumps(reply).encode("utf-8"), addr)

    def error_received(self, exc):
        log.warning("Socket error: %s", exc)


async def main(host: str, port: int):
    node_id = hashlib.sha1(uuid.uuid4().bytes).hexdigest()  # 160-bit, like Kademlia
    loop = asyncio.get_running_loop()
    transport, protocol = await loop.create_datagram_endpoint(
        lambda: ListenerProtocol(node_id),
        local_addr=(host, port),
    )
    try:
        while True:
            await asyncio.sleep(1)  # run forever, wakes every second so Ctrl+C works
    finally:
        log.info("Shutting down. Handled %d pings.", protocol.handled)
        transport.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="MeshWeaver UDP listener node")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=9000)
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s", datefmt="%H:%M:%S")
    try:
        asyncio.run(main(args.host, args.port))
    except KeyboardInterrupt:
        pass