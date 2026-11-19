
import asyncio
import json

from day9_wk2.peer import Peer
from day9_wk2.routing_table import RoutingTable, generate_node_id


class PeerDiscovery:

    def __init__(
        self,
        host="127.0.0.1",
        port=0,
        bootstrap_host="127.0.0.1",
        bootstrap_port=9200
    ):
        self.host = host
        self.port = port

        self.bootstrap_host = bootstrap_host
        self.bootstrap_port = bootstrap_port

        self.node_id = generate_node_id(
            f"{host}:{port}:{id(self)}"
        )

        self.routing_table = RoutingTable(
            self.node_id,
            k=20
        )

        self.discovered_peers = {}

    async def discover(self):
        try:
            reader, writer = await asyncio.open_connection(
                self.bootstrap_host,
                self.bootstrap_port
            )

            request = {
                "type": "JOIN",
                "node_id": self.node_id,
                "ip": self.host,
                "port": self.port
            }

            writer.write(
                (json.dumps(request) + "\n").encode()
            )

            await writer.drain()

            data = await asyncio.wait_for(
                reader.readline(),
                timeout=5
            )

            if not data:
                raise ConnectionError("Empty bootstrap response")

            response = json.loads(data.decode())

            if response.get("type") != "PEERS":
                raise ConnectionError(
                    response.get("message", "Peer discovery failed")
                )

            for peer_data in response.get("peers", []):
                peer = Peer(
                    node_id=peer_data["node_id"],
                    ip=peer_data["ip"],
                    port=peer_data["port"]
                )

                if peer.node_id != self.node_id:
                    self.routing_table.add_peer(peer)
                    self.discovered_peers[peer.node_id] = peer

            print(
                f"Node {self.node_id[:8]} discovered "
                f"{len(self.discovered_peers)} peer(s)"
            )

            return list(self.discovered_peers.values())

        except (
            OSError,
            asyncio.TimeoutError,
            ValueError,
            KeyError,
            TypeError
        ) as error:
            print(f"Discovery failed: {error}")
            return []

        finally:
            if "writer" in locals():
                writer.close()
                await writer.wait_closed()

    def get_discovered_peers(self):
        return list(self.discovered_peers.values())


async def main():
    node = PeerDiscovery(port=9301)

    peers = await node.discover()

    print("\nDiscovered peers:")

    for peer in peers:
        print(peer.to_dict())

    print("\nRouting table statistics:")
    print(node.routing_table.get_statistics())


if __name__ == "__main__":
    asyncio.run(main())
