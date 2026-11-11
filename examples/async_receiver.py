
import asyncio

HOST = "127.0.0.1"
PORT = 5003


class ReceiverProtocol(asyncio.DatagramProtocol):

    def connection_made(self, transport):
        self.transport = transport
        print(f"Async Node B listening on {HOST}:{PORT}")

    def datagram_received(self, data, address):
        message = data.decode()

        print(f"Message received from Node A: {message}")

        ack = b"ACK: Async message received successfully!"
        self.transport.sendto(ack, address)


async def main():
    loop = asyncio.get_running_loop()

    transport, protocol = await loop.create_datagram_endpoint(
        ReceiverProtocol,
        local_addr=(HOST, PORT)
    )

    try:
        await asyncio.Future()
    finally:
        transport.close()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nAsync receiver stopped.")
