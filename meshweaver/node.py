
import asyncio

from meshweaver.protocol import create_message, encode_message, decode_message


async def handle_client(reader, writer):
    address = writer.get_extra_info("peername")
    print(f"Connected to {address}")

    try:
        while True:
            data = await reader.readline()

            if not data:
                break

            try:
                message = decode_message(data.decode().strip())
                print(f"Received from {message['sender']}: {message['payload']}")

                response = create_message(
                    message_type="ack",
                    sender="MeshWeaver",
                    payload=f"Message received: {message['payload']}"
                )

                writer.write(encode_message(response).encode())
                await writer.drain()

            except Exception as error:
                print(f"Error processing message: {error}")

    finally:
        writer.close()
        await writer.wait_closed()
        print(f"Disconnected: {address}")


async def main():
    server = await asyncio.start_server(
        handle_client,
        "127.0.0.1",
        8888
    )

    print("MeshWeaver server running on port 8888")

    async with server:
        await server.serve_forever()


if __name__ == "__main__":
    asyncio.run(main())
