import asyncio


async def handle_client(reader, writer):
    address = writer.get_extra_info("peername")
    print(f"Connected to {address}")

    try:
        data = await reader.readline()
        message = data.decode().strip()

        print(f"Received: {message}")

        response = f"MeshWeaver received: {message}\n"
        writer.write(response.encode())
        await writer.drain()

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