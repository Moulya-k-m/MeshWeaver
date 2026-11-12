
import asyncio
from meshweaver.client import MeshClient
from meshweaver.protocol import create_message


async def main():
    client = MeshClient("127.0.0.1", 8888)

    await client.connect()
    print("Connected to MeshWeaver!")

    message = create_message(
        message_type="chat",
        sender="Moulya",
        payload="Hello MeshWeaver!"
    )

    await client.send(message)
    print("Message sent!")

    response = await client.receive()
    print("Server response:", response)

    await client.close()


asyncio.run(main())
