import asyncio


class Sender(asyncio.DatagramProtocol):

    def connection_made(self, transport):

        self.transport = transport
        self.finished = asyncio.get_running_loop().create_future()

        message = "Hello from Async Node A"

        self.transport.sendto(
            message.encode(),
            ("127.0.0.1", 5001)
        )

    def datagram_received(self, data, address):

        print("Response:", data.decode())

        if not self.finished.done():
            self.finished.set_result(True)

        self.transport.close()

    def error_received(self, error):
        print("Network error:", error)


async def main():

    loop = asyncio.get_running_loop()

    transport, protocol = await loop.create_datagram_endpoint(
        Sender,
        local_addr=("127.0.0.1", 0)
    )

    try:
        await asyncio.wait_for(
            protocol.finished,
            timeout=5
        )

    except asyncio.TimeoutError:
        print("ACK timeout")

    finally:
        transport.close()


asyncio.run(main())