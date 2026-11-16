
import asyncio
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "day5_wk1"))

from framing import read_msg, write_msg
from security import sign, verify
from serializer import serialize_call


def multiply(a, b):
    return a * b


async def send_request(port, message):
    reader, writer = await asyncio.open_connection(
        "127.0.0.1", port
    )

    try:
        await write_msg(writer, sign(message))
        response = await read_msg(reader)

        if not verify(response):
            raise ConnectionError("Invalid response signature")

        return response

    finally:
        writer.close()
        await writer.wait_closed()


async def main():

    print("STEP 1: Serializing function...")

    encoded = serialize_call(multiply, args=(10, 20))

    print("Function serialized!")

    print("\nSTEP 2: Submitting task to MeshWeaver...")

    response = await send_request(
        8001,
        {
            "type": "SUBMIT_TASK",
            "payload": {
                "operation": "REMOTE_CALL",
                "encoded": encoded
            }
        }
    )

    if response.get("type") != "TASK_ACCEPTED":
        print("Task submission failed:", response)
        return

    task_id = response["task_id"]

    print("Task accepted!")
    print("Task ID:", task_id)

    print("\nSTEP 3: Waiting for execution...")

    for attempt in range(20):

        result = await send_request(
            8001,
            {
                "type": "GET_RESULT",
                "task_id": task_id
            }
        )

        if result.get("status") == "COMPLETED":

            print("\nTask completed!")
            print("Result:", result.get("result"))

            assert result["result"]["value"] == 200

            print("\nREMOTE EXECUTION TEST PASSED!")
            return

        if result.get("status") == "FAILED":
            print("Task failed:", result.get("error"))
            return

        await asyncio.sleep(0.5)

    print("Task is still pending or running.")
    print("Check the node terminal.")


if __name__ == "__main__":
    asyncio.run(main())
