
import asyncio

from meshweaver.protocol import (
    create_message,
    encode_message,
    decode_message
)
from meshweaver.identity import NodeIdentity
from meshweaver.peer import Peer, PeerRegistry
from meshweaver.dht import DHT


def execute_task(payload):
    """Execute a supported remote task."""
    operation = payload.get("operation")
    args = payload.get("args", [])

    if operation == "add":
        return sum(args)

    elif operation == "multiply":
        result = 1
        for number in args:
            result *= number
        return result

    elif operation == "divide":
        if len(args) < 2:
            raise ValueError("Division requires at least two numbers")

        result = args[0]

        for number in args[1:]:
            if number == 0:
                raise ZeroDivisionError("Cannot divide by zero")
            result /= number

        return result

    raise ValueError(f"Unsupported operation: {operation}")


class MeshNode:
    """Represents a MeshWeaver node."""

    def __init__(self, host="127.0.0.1", port=8888, node_id=None):
        self.host = host
        self.port = port

        self.identity = NodeIdentity(node_id)
        self.peer_registry = PeerRegistry()
        self.server = None

        # DHT discovery and distributed storage.
        self.dht = DHT(self)

    def get_node_id(self):
        return self.identity.get_id()

    def add_peer(self, peer):
        if peer.node_id == self.get_node_id():
            raise ValueError("A node cannot register itself as a peer")

        self.peer_registry.add_peer(peer)

    def get_peers(self):
        return self.peer_registry.get_all_peers()

    async def handle_client(self, reader, writer):
        """Handle incoming TCP messages."""

        address = writer.get_extra_info("peername")
        print(f"Node {self.get_node_id()} connected to {address}")

        try:
            while True:
                data = await reader.readline()

                if not data:
                    break

                try:
                    message = decode_message(data.decode().strip())

                    print(
                        f"Received from {message['sender']}: "
                        f"{message['payload']}"
                    )

                    if message["type"] == "task":
                        try:
                            result = execute_task(message["payload"])

                            response = create_message(
                                "result",
                                self.get_node_id(),
                                {
                                    "status": "success",
                                    "result": result
                                }
                            )

                        except Exception as error:
                            response = create_message(
                                "result",
                                self.get_node_id(),
                                {
                                    "status": "error",
                                    "error": str(error)
                                }
                            )

                    elif message["type"] in {
                        "ping",
                        "find_node",
                        "store",
                        "find_value"
                    }:
                        response = await self.dht.handle_message(message)

                    else:
                        response = create_message(
                            "ack",
                            self.get_node_id(),
                            f"Message received: {message['payload']}"
                        )

                    writer.write(encode_message(response).encode())
                    await writer.drain()

                except Exception as error:
                    print(f"Error processing message: {error}")

        finally:
            writer.close()

            try:
                await writer.wait_closed()
            except OSError:
                pass

            print(f"Disconnected: {address}")

    async def start(self):
        """Start this node's TCP server."""

        if self.server is not None:
            raise RuntimeError("Node server is already running")

        self.server = await asyncio.start_server(
            self.handle_client,
            self.host,
            self.port
        )

        print(
            f"MeshWeaver node {self.get_node_id()} "
            f"running at {self.host}:{self.port}"
        )

    async def join_network(self, bootstrap_host, bootstrap_port,
                           bootstrap_node_id):
        """Join an existing MeshWeaver network."""

        bootstrap_peer = Peer(
            node_id=bootstrap_node_id,
            host=bootstrap_host,
            port=bootstrap_port
        )

        return await self.dht.join(bootstrap_peer)

    async def stop(self):
        """Stop this node's TCP server."""

        if self.server is not None:
            self.server.close()
            await self.server.wait_closed()
            self.server = None

            print(f"Node {self.get_node_id()} stopped")

    async def serve_forever(self):
        """Keep the node running."""

        if self.server is None:
            await self.start()

        async with self.server:
            await self.server.serve_forever()


async def main():
    node = MeshNode()

    try:
        await node.serve_forever()

    except KeyboardInterrupt:
        print("Shutting down MeshWeaver node...")

    finally:
        await node.stop()


if __name__ == "__main__":
    asyncio.run(main())


async def handle_client(reader, writer):
    """Backward-compatible standalone client handler."""

    address = writer.get_extra_info("peername")
    print(f"Connected to {address}")

    try:
        while True:
            data = await reader.readline()

            if not data:
                break

            try:
                message = decode_message(data.decode().strip())

                if message["type"] == "task":
                    try:
                        result = execute_task(message["payload"])

                        response = create_message(
                            "result",
                            "MeshWeaver",
                            {
                                "status": "success",
                                "result": result
                            }
                        )

                    except Exception as error:
                        response = create_message(
                            "result",
                            "MeshWeaver",
                            {
                                "status": "error",
                                "error": str(error)
                            }
                        )

                else:
                    response = create_message(
                        "ack",
                        "MeshWeaver",
                        f"Message received: {message['payload']}"
                    )

                writer.write(encode_message(response).encode())
                await writer.drain()

            except Exception as error:
                print(f"Error processing message: {error}")

    finally:
        writer.close()

        try:
            await writer.wait_closed()
        except OSError:
            pass
