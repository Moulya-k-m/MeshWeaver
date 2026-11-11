
import argparse
import asyncio
import logging

from framing import read_msg, write_msg

log = logging.getLogger("tcp_client")


async def request(reader, writer, message):
    await write_msg(writer, message)

    reply = await asyncio.wait_for(
        read_msg(reader),
        timeout=5
    )

    log.info("Sent %s -> got %s", message, reply)


async def main(host: str, port: int):
    reader, writer = await asyncio.open_connection(host, port)

    try:
        messages = [
            {"type": "HELLO", "name": "node B"},
            {"type": "ADD", "a": 20, "b": 22},
            {"type": "TIME"},
            {"type": "STATUS"},
            {"type": "NOPE"}
        ]

        for message in messages:
            await request(reader, writer, message)

    finally:
        writer.close()
        await writer.wait_closed()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="MeshWeaver TCP client node"
    )

    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=9100)

    args = parser.parse_args()

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(message)s",
        datefmt="%H:%M:%S"
    )

    asyncio.run(main(args.host, args.port))
