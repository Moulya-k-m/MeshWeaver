
import asyncio

from meshweaver.client import MeshClient
from meshweaver.protocol import create_message


async def main():
    client = MeshClient("127.0.0.1", 8888)

    await client.connect()
    print("Connected to MeshWeaver node")

    task = create_message(
        message_type="task",
        sender="Moulya",
        payload={
"operation": "divide",
"args": [10, 2]
        }
    )

    await client.send(task)
    print("Task sent:", task["payload"])

    response = await client.receive()
    print("Remote result:", response["payload"])

    await client.close()


if __name__ == "__main__":
    asyncio.run(main())
