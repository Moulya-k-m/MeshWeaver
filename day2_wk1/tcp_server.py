
import argparse
import asyncio
import logging
from datetime import datetime, timezone

from framing import read_msg, write_msg

log = logging.getLogger("tcp_server")


async def handle_client(reader, writer):
    addr = writer.get_extra_info("peername")
    log.info("Connected: %s", addr)

    try:
        while True:
            msg = await asyncio.wait_for(read_msg(reader), timeout=30)
            log.info("Got %s from %s", msg, addr)

            kind = msg.get("type")

            if kind == "HELLO":
                reply = {
                    "type": "HELLO_ACK",
                    "text": f"Hello, {msg.get('name', 'stranger')}!"
                }

            elif kind == "ADD":
                reply = {
                    "type": "RESULT",
                    "value": msg["a"] + msg["b"]
                }

            elif kind == "TIME":
                reply = {
                    "type": "TIME_RESPONSE",
                    "time": datetime.now(timezone.utc).isoformat()
                }

            else:
                reply = {
                    "type": "ERROR",
                    "reason": f"unknown type {kind!r}"
                }

            await write_msg(writer, reply)

    except asyncio.IncompleteReadError:
        log.info("Client %s disconnected", addr)

    except asyncio.TimeoutError:
        log.warning("Client %s idle for 30s, closing", addr)

    except (ValueError, KeyError, TypeError) as exc:
        log.warning("Bad message from %s: %s", addr, exc)

    finally:
        writer.close()
        await writer.wait_closed()


async def main(host: str, port: int):
    server = await asyncio.start_server(handle_client, host, port)

    log.info("TCP server listening on %s", server.sockets[0].getsockname())

    async with server:
        await server.serve_forever()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="MeshWeaver TCP server node")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=9100)

    args = parser.parse_args()

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(message)s",
        datefmt="%H:%M:%S"
    )

    try:
        asyncio.run(main(args.host, args.port))
    except KeyboardInterrupt:
        pass
