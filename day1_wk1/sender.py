
import argparse
import asyncio
import hashlib
import json
import logging
import time
import uuid

log = logging.getLogger("sender")


class SenderProtocol(asyncio.DatagramProtocol):
    def __init__(self, node_id: str):
        self.node_id = node_id
        self.transport = None
        self.pending: dict[int, asyncio.Future] = {}

    def connection_made(self, transport):
        self.transport = transport

    def send_ping(self, seq: int) -> asyncio.Future:
        fut = asyncio.get_running_loop().create_future()
        self.pending[seq] = fut

        msg = {
            "type": "PING",
            "seq": seq,
            "node_id": self.node_id,
            "ts": time.time()
        }

        self.transport.sendto(json.dumps(msg).encode("utf-8"))
        return fut

    def datagram_received(self, data, addr):
        try:
            msg = json.loads(data.decode("utf-8"))

            if not isinstance(msg, dict) or msg.get("type") != "PONG":
                raise ValueError("not a PONG message")

            seq = msg["seq"]

        except (ValueError, KeyError) as exc:
            log.warning("Dropped bad packet from %s: %s", addr, exc)
            return

        fut = self.pending.pop(seq, None)

        if fut is not None and not fut.done():
            fut.set_result(msg)

    def error_received(self, exc):
        log.debug("Socket error: %s", exc)


async def main(host: str, port: int, count: int, timeout: float):

    node_id = hashlib.sha1(uuid.uuid4().bytes).hexdigest()
    loop = asyncio.get_running_loop()

    transport, protocol = await loop.create_datagram_endpoint(
        lambda: SenderProtocol(node_id),
        remote_addr=(host, port),
    )

    log.info(
        "Node %s pinging %s:%d (%d pings)",
        node_id[:8], host, port, count
    )

    rtts = []
    jitters = []

    try:
        for seq in range(1, count + 1):

            start = time.perf_counter()
            fut = protocol.send_ping(seq)

            try:
                reply = await asyncio.wait_for(fut, timeout=timeout)

                rtt_ms = (time.perf_counter() - start) * 1000
                rtts.append(rtt_ms)

                if len(rtts) > 1:
                    jitter = abs(rtts[-1] - rtts[-2])
                    jitters.append(jitter)

                log.info(
                    "PONG seq=%d from node %s rtt=%.2f ms",
                    seq, reply["node_id"][:8], rtt_ms
                )

            except asyncio.TimeoutError:
                protocol.pending.pop(seq, None)

                log.warning(
                    "seq=%d: no reply within %.1fs",
                    seq, timeout
                )

            await asyncio.sleep(0.2)

    finally:
        transport.close()

    lost = count - len(rtts)
    packet_loss = (lost / count) * 100

    log.info(
        "Summary: sent=%d received=%d lost=%d (%.0f%% loss)",
        count, len(rtts), lost, packet_loss
    )

    avg_rtt = sum(rtts) / len(rtts) if rtts else float("inf")
    avg_jitter = sum(jitters) / len(jitters) if jitters else 0.0

    if rtts:
        log.info(
            "RTT ms: min=%.2f avg=%.2f max=%.2f",
            min(rtts), avg_rtt, max(rtts)
        )

    if jitters:
        log.info("Average Jitter: %.2f ms", avg_jitter)

    # Network health classification

    if (
        not rtts
        or packet_loss >= 5
        or avg_rtt >= 250
        or avg_jitter >= 50
    ):
        status = "POOR"

    elif (
        packet_loss > 0
        or avg_rtt >= 100
        or avg_jitter >= 20
    ):
        status = "UNSTABLE"

    else:
        status = "HEALTHY"

    log.info("Network Health: %s", status)


if __name__ == "__main__":

    parser = argparse.ArgumentParser(
        description="MeshWeaver UDP ping node"
    )

    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=9000)
    parser.add_argument("--count", type=int, default=5)
    parser.add_argument("--timeout", type=float, default=2.0)

    args = parser.parse_args()

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(message)s",
        datefmt="%H:%M:%S"
    )

    asyncio.run(main(args.host, args.port, args.count, args.timeout))
