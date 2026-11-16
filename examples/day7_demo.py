
import asyncio
from meshweaver.client import MeshClient
from meshweaver.protocol import create_message


async def main():
    client = MeshClient("127.0.0.1", 8888)

    await client.connect()
    print("Connected to MeshWeaver server!")

    
    tasks = [
    {"operation": "add", "args": [10, 20]},
    {"operation": "divide", "args": [10, 2]},
]

    for payload in tasks:
        task = create_message(
            message_type="task",
            sender="Moulya",
            payload=payload
        )

        await client.send(task)
        response = await client.receive()
        print("Server response:", response)

    await client.close()
    print("Connection closed!")


if __name__ == "__main__":
    asyncio.run(main())
