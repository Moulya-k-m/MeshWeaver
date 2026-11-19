import asyncio


class Receiver(asyncio.DatagramProtocol):

    def connection_made(self, transport):
        self.transport = transport
        print("Async Receiver is running...")

    def datagram_received(self, data, address):

        message = data.decode()

        print("Received:", message)

        response = "ACK: Async message received"

        self.transport.sendto(
            response.encode(),
            address
        )


async def main():

    loop = asyncio.get_running_loop()

    transport, protocol = await loop.create_datagram_endpoint(
        Receiver,
        local_addr=("127.0.0.1", 5001)
    )

    try:
        await asyncio.Future()

    finally:
        transport.close()


asyncio.run(main())