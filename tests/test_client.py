
import asyncio

from meshweaver.client import MeshClient
from meshweaver.node import handle_client
from meshweaver.protocol import create_message


def test_client_server_communication():
    async def run():
        server = await asyncio.start_server(
            handle_client, "127.0.0.1", 0
        )

        port = server.sockets[0].getsockname()[1]

        async with server:
            client = MeshClient("127.0.0.1", port)
            await client.connect()

            message = create_message(
                "chat", "Moulya", "Hello MeshWeaver!"
            )

            await client.send(message)
            response = await client.receive()

            assert response["type"] == "ack"
            assert response["sender"] == "MeshWeaver"
            assert response["payload"] == "Message received: Hello MeshWeaver!"

            await client.close()

            server.close()
            await server.wait_closed()

    asyncio.run(run())


def test_multiple_messages():
    async def run():
        server = await asyncio.start_server(
            handle_client, "127.0.0.1", 0
        )

        port = server.sockets[0].getsockname()[1]

        async with server:
            client = MeshClient("127.0.0.1", port)
            await client.connect()

            for i in range(3):
                message = create_message(
                    "chat", "Moulya", f"Message {i + 1}"
                )

                await client.send(message)
                response = await client.receive()

                assert response["type"] == "ack"
                assert response["payload"] == f"Message received: Message {i + 1}"

            await client.close()

            server.close()
            await server.wait_closed()

    asyncio.run(run())

