
import asyncio
import logging

from framing import read_msg, write_msg

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
    datefmt="%H:%M:%S"
)


async def test_client(name):
    reader, writer = await asyncio.open_connection(
        "127.0.0.1", 9100
    )

    try:
        logging.info("%s connected", name)

        messages = [
            {"type": "HELLO", "name": name},
            {"type": "STATUS"}
        ]

        for message in messages:
            await write_msg(writer, message)

            reply = await asyncio.wait_for(
                read_msg(reader), timeout=5
            )

            logging.info("%s received: %s", name, reply)

    finally:
        writer.close()
        await writer.wait_closed()
        logging.info("%s disconnected", name)


async def main():
    await asyncio.gather(
        test_client("Client A"),
        test_client("Client B")
    )


if __name__ == "__main__":
    asyncio.run(main())
