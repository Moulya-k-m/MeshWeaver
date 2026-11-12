
import asyncio
from meshweaver.protocol import encode_message, decode_message


class MeshClient:
    def __init__(self, host, port):
        self.host = host
        self.port = port

    async def connect(self):
        self.reader, self.writer = await asyncio.open_connection(
            self.host, self.port
        )

    async def send(self, message):
        data = encode_message(message)
        self.writer.write(data.encode())
        await self.writer.drain()

    async def receive(self):
        data = await self.reader.readline()
        return decode_message(data.decode().strip())

    async def close(self):
        self.writer.close()
        await self.writer.wait_closed()
