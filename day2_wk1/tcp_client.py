import argparse
import asyncio
import logging

from framing import read_msg, write_msg

log = logging.getLogger("tcp_client")


async def request(reader, writer, msg: dict, timeout: float = 5.0) -> dict:
    await write_msg(writer, msg)
    return await asyncio.wait_for(read_msg(reader), timeout=timeout)


async def main(host: str, port: int):
    try:
        reader, writer = await asyncio.wait_for(asyncio.open_connection(host, port), timeout=5)
    except (OSError, asyncio.TimeoutError) as exc:
        log.error("Could not connect to %s:%d (%s). Is the server running?", host, port, exc)
        return

    try:
        for msg in [
            {"type": "HELLO", "name": "node B"},
            {"type": "ADD", "a": 20, "b": 22},
            {"type": "TIME"},
            {"type": "NOPE"},
        ]:
            reply = await request(reader, writer, msg)
            log.info("Sent %s -> got %s", msg, reply)
    except (asyncio.TimeoutError, asyncio.IncompleteReadError) as exc:
        log.error("Server problem: %r", exc)
    finally:
        writer.close()
        await writer.wait_closed()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="MeshWeaver TCP client node")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=9100)
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s", datefmt="%H:%M:%S")
    asyncio.run(main(args.host, args.port))

    