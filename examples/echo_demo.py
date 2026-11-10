import asyncio


async def main():
    reader, writer = await asyncio.open_connection(
        "127.0.0.1",
        8888
    )

    message = "Hello MeshWeaver!"

    print(f"Sending: {message}")

    writer.write(f"{message}\n".encode())
    await writer.drain()

    response = await reader.readline()
    print(f"Response: {response.decode().strip()}")

    writer.close()
    await writer.wait_closed()


if __name__ == "__main__":
    asyncio.run(main())