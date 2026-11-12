import json
import struct

MAX_MSG = 1_000_000  # refuse messages over 1 MB


async def read_msg(reader) -> dict:
    header = await reader.readexactly(4)          # exactly 4 bytes
    (length,) = struct.unpack("!I", header)       # "!I" = 4-byte big-endian number
    if length > MAX_MSG:
        raise ValueError(f"message too big: {length} bytes")
    body = await reader.readexactly(length)       # exactly `length` bytes
    msg = json.loads(body.decode("utf-8"))
    if not isinstance(msg, dict):
        raise ValueError("message is not a JSON object")
    return msg


async def write_msg(writer, msg: dict) -> None:
    body = json.dumps(msg).encode("utf-8")
    writer.write(struct.pack("!I", len(body)) + body)
    await writer.drain()                          # wait until data is actually sent