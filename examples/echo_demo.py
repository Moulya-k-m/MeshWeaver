
import asyncio

from meshweaver.protocol import create_message, encode_message, decode_message


async def main():
    reader, writer = await asyncio.open_connection(
        "127.0.0.1",
        8888
    )

    messages = [
        "Hello MeshWeaver!",
        "Testing message 2",
        "Testing message 3"
    ]

    for text in messages:
        message = create_message(
            message_type="chat",
            sender="Moulya",
            payload=text
        )

        writer.write(encode_message(message).encode())
        await writer.drain()

        response = await reader.readline()
        decoded_response = decode_message(response.decode().strip())

        print(f"Response: {decoded_response}")

    writer.close()
    await writer.wait_closed()


if __name__ == "__main__":
    asyncio.run(main())
