
import asyncio
import json

from day9_wk2.peer import Peer
from day9_wk2.routing_table import validate_node_id


class FindNodeServer:

    def __init__(self, host, port, node_id, routing_table):
        self.host = host
        self.port = port
        self.node_id = validate_node_id(node_id)
        self.routing_table = routing_table

    async def handle_client(self, reader, writer):
        try:
            data = await asyncio.wait_for(
                reader.readline(),
                timeout=5
            )

            if not data:
                return

            request = json.loads(data.decode())

            if request.get("type") != "FIND_NODE":
                response = {
                    "type": "ERROR",
                    "message": "Invalid request type"
                }
            else:
                target_id = validate_node_id(
                    request["target_node_id"]
                )

                closest_peers = (
                    self.routing_table.get_closest_nodes(
                        target_id,
                        count=20
                    )
                )

                response = {
                    "type": "NODES",
                    "target_node_id": target_id,
                    "peers": [
                        peer.to_dict()
                        for peer in closest_peers
                    ]
                }

            writer.write(
                (json.dumps(response) + "\n").encode()
            )
            await writer.drain()

        except asyncio.TimeoutError:
            pass

        except (
            ValueError,
            KeyError,
            TypeError,
            json.JSONDecodeError
        ) as error:
            response = {
                "type": "ERROR",
                "message": str(error)
            }

            writer.write(
                (json.dumps(response) + "\n").encode()
            )
            await writer.drain()

        finally:
            writer.close()
            await writer.wait_closed()


class FindNodeClient:

    def __init__(self, timeout=5):
        self.timeout = timeout

    async def find_node(self, host, port, target_node_id):

        try:
            target_node_id = validate_node_id(target_node_id)

            reader, writer = await asyncio.wait_for(
                asyncio.open_connection(host, port),
                timeout=self.timeout
            )

            request = {
                "type": "FIND_NODE",
                "target_node_id": target_node_id
            }

            writer.write(
                (json.dumps(request) + "\n").encode()
            )
            await writer.drain()

            data = await asyncio.wait_for(
                reader.readline(),
                timeout=self.timeout
            )

            if not data:
                raise ConnectionError("Empty response")

            response = json.loads(data.decode())

            if response.get("type") != "NODES":
                raise ConnectionError(
                    response.get("message", "Lookup failed")
                )

            peers = []

            for peer_data in response.get("peers", []):
                peers.append(
                    Peer(
                        node_id=peer_data["node_id"],
                        ip=peer_data["ip"],
                        port=peer_data["port"],
                        last_seen=peer_data.get("last_seen")
                    )
                )

            return peers

        except (
            OSError,
            asyncio.TimeoutError,
            ValueError,
            KeyError,
            TypeError,
            json.JSONDecodeError,
            ConnectionError
        ) as error:
            print(f"FIND_NODE failed: {error}")
            return []

        finally:
            if "writer" in locals():
                writer.close()
                await writer.wait_closed()
