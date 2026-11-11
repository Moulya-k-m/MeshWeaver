
import asyncio

from meshweaver.protocol import create_message, encode_message, decode_message


async def client(client_name):
    reader, writer = await asyncio.open_connection(
        "127.0.0.1",
        8888
    )

    message = create_message(
        message_type="chat",
        sender=client_name,
        payload=f"Hello from {client_name}!"
    )

    writer.write(encode_message(message).encode())
    await writer.drain()

    response = await reader.readline()
    decoded_response = decode_message(response.decode().strip())

    print(f"{client_name} received: {decoded_response}")

    writer.close()
    await writer.wait_closed()


async def main():
    await asyncio.gather(
        client("Node-A"),
        client("Node-B"),
        client("Node-C")
    )


if __name__ == "__main__":
    asyncio.run(main())
