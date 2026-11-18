"""Async UDP task broker for trusted localhost demonstration only.

Never expose this pickle-based prototype to untrusted peers.
"""
import asyncio
import base64
import json
import uuid
from collections import OrderedDict

import cloudpickle

MAX_PACKET = 60000


def encode(message):
    payload = json.dumps(message, separators=(",", ":")).encode("utf-8")
    if len(payload) > MAX_PACKET:
        raise ValueError("UDP message exceeds 60000-byte demo limit")
    return payload


def decode(payload):
    if len(payload) > MAX_PACKET:
        raise ValueError("Oversized packet")
    message = json.loads(payload.decode("utf-8"))
    if not isinstance(message, dict):
        raise ValueError("Expected JSON object")
    return message


class Worker(asyncio.DatagramProtocol):
    def __init__(self):
        self.transport = None
        self.completed = OrderedDict()
        self.tasks = set()

    def connection_made(self, transport):
        self.transport = transport

    def datagram_received(self, data, addr):
        if addr[0] != "127.0.0.1":
            return
        try:
            msg = decode(data)
            if msg.get("type") != "task" or not isinstance(msg.get("id"), str):
                raise ValueError("Invalid task message")
            task_id = msg["id"]
            if len(task_id) > 64:
                raise ValueError("Invalid task id")
            if task_id in self.completed:
                self.transport.sendto(self.completed[task_id], addr)
                return
            # ACK is informational; the result remains authoritative.
            self.transport.sendto(encode({"type": "ack", "id": task_id}), addr)
            task = asyncio.create_task(self.execute(msg, addr))
            self.tasks.add(task)
            task.add_done_callback(self.tasks.discard)
        except (ValueError, UnicodeError, KeyError, TypeError, json.JSONDecodeError):
            return

    async def execute(self, msg, addr):
        task_id = msg["id"]
        try:
            raw = base64.b64decode(msg["payload"], validate=True)
            if len(raw) > 45000:
                raise ValueError("Task payload too large")
            function, args, kwargs = cloudpickle.loads(raw)
            if not callable(function) or not isinstance(args, tuple) or not isinstance(kwargs, dict):
                raise ValueError("Invalid function arguments")
            if asyncio.iscoroutinefunction(function):
                result = await function(*args, **kwargs)
            else:
                result = await asyncio.to_thread(function, *args, **kwargs)
            response = {"type": "result", "id": task_id, "ok": True, "value": result}
            packet = encode(response)
        except Exception as exc:
            packet = encode({"type": "result", "id": task_id, "ok": False,
                             "error": f"{type(exc).__name__}: {str(exc)[:200]}"})
        self.completed[task_id] = packet
        if len(self.completed) > 256:
            self.completed.popitem(last=False)
        self.transport.sendto(packet, addr)


class Client(asyncio.DatagramProtocol):
    def __init__(self):
        self.transport = None
        self.pending = {}

    def connection_made(self, transport):
        self.transport = transport

    def datagram_received(self, data, addr):
        if addr[0] != "127.0.0.1":
            return
        try:
            msg = decode(data)
            if msg.get("type") != "result":
                return
            future = self.pending.get(msg.get("id"))
            if future is not None and not future.done():
                future.set_result(msg)
        except (ValueError, UnicodeError, TypeError):
            return

    async def submit(self, function, *args, timeout=2.0, retries=2, **kwargs):
        task_id = uuid.uuid4().hex
        serialized = cloudpickle.dumps((function, args, kwargs))
        packet = encode({"type": "task", "id": task_id,
                         "payload": base64.b64encode(serialized).decode("ascii")})
        loop = asyncio.get_running_loop()
        future = loop.create_future()
        self.pending[task_id] = future
        try:
            for attempt in range(retries + 1):
                self.transport.sendto(packet)
                try:
                    response = await asyncio.wait_for(asyncio.shield(future), timeout)
                    if not response.get("ok"):
                        raise RuntimeError(response.get("error", "Remote execution failed"))
                    return response.get("value")
                except asyncio.TimeoutError:
                    if attempt == retries:
                        raise TimeoutError(f"Task {task_id} timed out") from None
        finally:
            self.pending.pop(task_id, None)


async def start_worker(port=9998):
    loop = asyncio.get_running_loop()
    return await loop.create_datagram_endpoint(Worker, local_addr=("127.0.0.1", port))


async def start_client(port=9998):
    loop = asyncio.get_running_loop()
    return await loop.create_datagram_endpoint(Client, remote_addr=("127.0.0.1", port))
