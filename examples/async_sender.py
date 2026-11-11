
import asyncio

HOST = "127.0.0.1"
PORT = 5003


class SenderProtocol(asyncio.DatagramProtocol):

    def __init__(self, loop):
        self.loop = loop
        self.response_future = loop.create_future()

    def connection_made(self, transport):
        self.transport = transport

        message = "Hello from Async MeshWeaver Node A!"
        self.transport.sendto(message.encode())

        print("Async message sent to Node B!")

    def datagram_received(self, data, address):
        response = data.decode()

        print("Response from Node B:", response)

        if not self.response_future.done():
            self.response_future.set_result(response)

    def error_received(self, exc):
        print("UDP error:", exc)


async def main():
    loop = asyncio.get_running_loop()

    transport, protocol = await loop.create_datagram_endpoint(
        lambda: SenderProtocol(loop),
        remote_addr=(HOST, PORT)
    )

    try:
        await asyncio.wait_for(protocol.response_future, timeout=5)
    except asyncio.TimeoutError:
        print("No response received. Request timed out.")
    finally:
        transport.close()


if __name__ == "__main__":
    asyncio.run(main())
