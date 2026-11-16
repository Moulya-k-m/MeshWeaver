
import asyncio
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "day5_wk1"))

from framing import read_msg, write_msg
from security import sign, verify


async def main():
    reader, writer = await asyncio.open_connection(
        "127.0.0.1", 8001
    )

    try:
        # Submit several tasks to Node 1.
        for i in range(8):
            await write_msg(
                writer,
                sign({
                    "type": "SUBMIT_TASK",
                    "payload": {
                        "operation": "ECHO",
                        "value": f"Load test {i}"
                    }
                })
            )

            response = await read_msg(reader)

            if not verify(response):
                raise RuntimeError("Invalid response signature")

            print("Submitted:", response)

            await asyncio.sleep(0.1)

    finally:
        writer.close()
        await writer.wait_closed()


if __name__ == "__main__":
    asyncio.run(main())

