
import asyncio
import json

from day9_wk2.peer import Peer
from day9_wk2.routing_table import RoutingTable, generate_node_id


class BootstrapServer:
    def __init__(self, host="127.0.0.1", port=9200):
        self.host = host
        self.port = port

        self.node_id = generate_node_id(
            f"{host}:{port}"
        )

        self.routing_table = RoutingTable(
            self.node_id,
            k=20
        )

    async def handle_client(self, reader, writer):
        try:
            data = await asyncio.wait_for(
                reader.readline(),
                timeout=5
            )

            if not data:
                return

            request = json.loads(data.decode())

            if request.get("type") != "JOIN":
                response = {
                    "type": "ERROR",
                    "message": "Invalid request"
                }
            else:
                node_id = request["node_id"]
                ip = request["ip"]
                port = request["port"]

                new_peer = Peer(
                    node_id=node_id,
                    ip=ip,
                    port=port
                )

                result = self.routing_table.add_peer(
                    new_peer
                )

                peers = [
                    peer.to_dict()
                    for peer in self.routing_table.get_all_peers()
                    if peer.node_id != node_id
                ]

                peers.append(
                    Peer(
                        self.node_id,
                        self.host,
                        self.port
                    ).to_dict()
                )

                response = {
                    "type": "PEERS",
                    "status": result,
                    "peers": peers
                }

            writer.write(
                (json.dumps(response) + "\n").encode()
            )

            await writer.drain()

        except (ValueError, KeyError, TypeError, json.JSONDecodeError) as error:
            response = {
                "type": "ERROR",
                "message": str(error)
            }

            writer.write(
                (json.dumps(response) + "\n").encode()
            )

            await writer.drain()

        except asyncio.TimeoutError:
            pass

        finally:
            writer.close()
            await writer.wait_closed()

    async def start(self):
        server = await asyncio.start_server(
            self.handle_client,
            self.host,
            self.port
        )

        print(
            f"Bootstrap server running at "
            f"{self.host}:{self.port}"
        )

        async with server:
            await server.serve_forever()


if __name__ == "__main__":
    bootstrap = BootstrapServer()

    try:
        asyncio.run(bootstrap.start())
    except KeyboardInterrupt:
        print("\nBootstrap server stopped.")
