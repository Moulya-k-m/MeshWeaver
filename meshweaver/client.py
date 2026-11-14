
import asyncio
from meshweaver.protocol import encode_message, decode_message


class MeshClient:
    def __init__(self, host, port, timeout=10):
        self.host = host
        self.port = port
        self.timeout = timeout
        self.reader = None
        self.writer = None

    async def connect(self):
        self.reader, self.writer = await asyncio.wait_for(
            asyncio.open_connection(self.host, self.port),
            timeout=self.timeout
        )

    async def send(self, message):
        if not self.writer or self.writer.is_closing():
            raise ConnectionError("Client is not connected")

        data = encode_message(message)
        self.writer.write(data.encode())
        await asyncio.wait_for(
            self.writer.drain(),
            timeout=self.timeout
        )

    async def receive(self):
        if not self.reader:
            raise ConnectionError("Client is not connected")

        data = await asyncio.wait_for(
            self.reader.readline(),
            timeout=self.timeout
        )

        if not data:
            raise ConnectionError("Server disconnected")

        return decode_message(data.decode().strip())

    async def close(self):
        if self.writer:
            self.writer.close()
            await self.writer.wait_closed()
            self.reader = None
            self.writer = None
