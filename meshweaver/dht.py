
import asyncio
import hashlib

from meshweaver.peer import Peer
from meshweaver.protocol import create_message, encode_message, decode_message


K = 20
ALPHA = 3
ID_BITS = 256


def hash_node_id(node_id):
    """Convert any node ID into a 256-bit integer."""
    return int.from_bytes(
        hashlib.sha256(str(node_id).encode("utf-8")).digest(),
        byteorder="big"
    )


def xor_distance(node_id_a, node_id_b):
    """Calculate the XOR distance between two node IDs."""
    return hash_node_id(node_id_a) ^ hash_node_id(node_id_b)


class RoutingTable:
    """Kademlia-inspired routing table with XOR-distance buckets."""

    def __init__(self, node_id, bucket_size=K):
        self.node_id = node_id
        self.bucket_size = bucket_size

        # 256 buckets, one for each possible XOR-distance bit.
        self.buckets = [[] for _ in range(ID_BITS)]

    def bucket_index(self, peer_id):
        """Determine the bucket for a peer."""
        distance = xor_distance(self.node_id, peer_id)

        if distance == 0:
            return None

        return distance.bit_length() - 1

    def add_peer(self, peer):
        """Add or refresh a peer in the appropriate bucket."""
        if not isinstance(peer, Peer):
            raise TypeError("Expected a Peer object")

        index = self.bucket_index(peer.node_id)

        if index is None:
            return False

        bucket = self.buckets[index]

        for existing in bucket:
            if existing.node_id == peer.node_id:
                bucket.remove(existing)
                bucket.append(peer)
                return True

        if len(bucket) >= self.bucket_size:
            return False

        bucket.append(peer)
        return True

    def remove_peer(self, node_id):
        """Remove a peer from its routing bucket."""
        index = self.bucket_index(node_id)

        if index is None:
            return False

        bucket = self.buckets[index]

        for peer in bucket:
            if peer.node_id == node_id:
                bucket.remove(peer)
                return True

        return False

    def get_all_peers(self):
        """Return every peer in the routing table."""
        peers = []

        for bucket in self.buckets:
            peers.extend(bucket)

        return peers

    def find_closest(self, target_id, count=K):
        """Return the closest known peers to a target ID."""
        peers = self.get_all_peers()

        peers.sort(
            key=lambda peer: xor_distance(peer.node_id, target_id)
        )

        return peers[:count]

    def __len__(self):
        return sum(len(bucket) for bucket in self.buckets)


class DHT:
    """Distributed hash table for MeshWeaver peer discovery."""

    def __init__(self, node):
        self.node = node
        self.node_id = node.get_node_id()

        self.routing_table = RoutingTable(self.node_id)

        # Local DHT key-value storage.
        self.storage = {}

    def add_peer(self, peer):
        """Add a peer to both the registry and routing table."""
        if peer.node_id == self.node_id:
            return False

        try:
            self.node.add_peer(peer)
        except ValueError:
            # The peer may already exist in the registry.
            pass

        return self.routing_table.add_peer(peer)

    def get_peers(self):
        """Return all known routing-table peers."""
        return self.routing_table.get_all_peers()

    def _request_payload(self, payload=None):
        """Attach this node's advertised address to a request."""
        result = dict(payload or {})

        result["requester"] = {
            "node_id": self.node_id,
            "host": self.node.host,
            "port": self.node.port
        }

        return result

    async def _rpc(self, peer, message_type, payload=None):
        """Send one request to another MeshWeaver node."""
        writer = None

        try:
            reader, writer = await asyncio.wait_for(
                asyncio.open_connection(peer.host, peer.port),
                timeout=5
            )

            message = create_message(
                message_type=message_type,
                sender=self.node_id,
                payload=self._request_payload(payload)
            )

            writer.write(encode_message(message).encode())
            await writer.drain()

            response_data = await asyncio.wait_for(
                reader.readline(),
                timeout=5
            )

            if not response_data:
                return None

            return decode_message(response_data.decode().strip())

        except (OSError, asyncio.TimeoutError, ValueError):
            return None

        finally:
            if writer is not None:
                writer.close()

                try:
                    await writer.wait_closed()
                except OSError:
                    pass

    async def handle_message(self, message):
        """Process an incoming DHT request."""
        message_type = message["type"]
        payload = message.get("payload", {})

        requester = payload.get("requester")

        if requester:
            try:
                peer = Peer(
                    node_id=requester["node_id"],
                    host=requester["host"],
                    port=requester["port"]
                )

                self.add_peer(peer)

            except (KeyError, TypeError, ValueError):
                pass

        if message_type == "ping":
            result = {"status": "alive"}

        elif message_type == "find_node":
            target_id = payload.get("target_id")

            if not target_id:
                result = {"status": "error", "error": "Missing target_id"}
            else:
                closest = self.routing_table.find_closest(target_id)

                result = {
                    "status": "success",
                    "nodes": [
                        {
                            "node_id": peer.node_id,
                            "host": peer.host,
                            "port": peer.port
                        }
                        for peer in closest
                    ]
                }

        elif message_type == "store":
            key = payload.get("key")

            if key is None or "value" not in payload:
                result = {
                    "status": "error",
                    "error": "Missing key or value"
                }
            else:
                self.storage[str(key)] = payload["value"]

                result = {
                    "status": "success",
                    "stored": True
                }

        elif message_type == "find_value":
            key = payload.get("key")

            if key is None:
                result = {
                    "status": "error",
                    "error": "Missing key"
                }
            elif str(key) in self.storage:
                result = {
                    "status": "success",
                    "found": True,
                    "value": self.storage[str(key)]
                }
            else:
                closest = self.routing_table.find_closest(str(key))

                result = {
                    "status": "success",
                    "found": False,
                    "nodes": [
                        {
                            "node_id": peer.node_id,
                            "host": peer.host,
                            "port": peer.port
                        }
                        for peer in closest
                    ]
                }

        else:
            result = {
                "status": "error",
                "error": f"Unknown DHT operation: {message_type}"
            }

        return create_message(
            message_type="dht_response",
            sender=self.node_id,
            payload=result
        )

    async def join(self, bootstrap_peer):
        """Join an existing mesh through a bootstrap peer."""
        if not isinstance(bootstrap_peer, Peer):
            raise TypeError("Expected a Peer bootstrap node")

        self.add_peer(bootstrap_peer)

        response = await self._rpc(
            bootstrap_peer,
            "ping"
        )

        if response is None:
            raise ConnectionError(
                f"Could not connect to bootstrap node "
                f"{bootstrap_peer.host}:{bootstrap_peer.port}"
            )

        # Discover nodes closest to our own node ID.
        await self.find_node(self.node_id)

        return self.get_peers()

    async def find_node(self, target_id):
        """Iteratively discover nodes closest to a target ID."""
        known = {
            peer.node_id: peer
            for peer in self.routing_table.find_closest(target_id)
        }

        queried = set()

        while True:
            candidates = [
                peer for peer in known.values()
                if peer.node_id not in queried
            ]

            candidates.sort(
                key=lambda peer: xor_distance(peer.node_id, target_id)
            )

            batch = candidates[:ALPHA]

            if not batch:
                break

            for peer in batch:
                queried.add(peer.node_id)

            responses = await asyncio.gather(
                *[
                    self._rpc(
                        peer,
                        "find_node",
                        {"target_id": target_id}
                    )
                    for peer in batch
                ]
            )

            for response in responses:
                if response is None:
                    continue

                payload = response.get("payload", {})

                for item in payload.get("nodes", []):
                    try:
                        discovered = Peer(
                            node_id=item["node_id"],
                            host=item["host"],
                            port=item["port"]
                        )

                        if discovered.node_id == self.node_id:
                            continue

                        self.add_peer(discovered)
                        known[discovered.node_id] = discovered

                    except (KeyError, TypeError, ValueError):
                        continue

        return self.routing_table.find_closest(target_id)

    async def store(self, key, value):
        """Store a value locally and replicate it to nearby peers."""
        key = str(key)

        # Always retain a local copy.
        self.storage[key] = value

        closest = self.routing_table.find_closest(key)

        if not closest:
            return True

        responses = await asyncio.gather(
            *[
                self._rpc(
                    peer,
                    "store",
                    {"key": key, "value": value}
                )
                for peer in closest
            ]
        )

        return any(
            response is not None
            and response.get("payload", {}).get("stored") is True
            for response in responses
        ) or True

    async def find_value(self, key):
        """Find a value locally or search remote peers."""
        key = str(key)

        if key in self.storage:
            return self.storage[key]

        candidates = self.routing_table.find_closest(key)
        queried = set()

        while candidates:
            candidates.sort(
                key=lambda peer: xor_distance(peer.node_id, key)
            )

            batch = [
                peer for peer in candidates
                if peer.node_id not in queried
            ][:ALPHA]

            if not batch:
                break

            for peer in batch:
                queried.add(peer.node_id)

            responses = await asyncio.gather(
                *[
                    self._rpc(peer, "find_value", {"key": key})
                    for peer in batch
                ]
            )

            for response in responses:
                if response is None:
                    continue

                payload = response.get("payload", {})

                if payload.get("found"):
                    self.storage[key] = payload["value"]
                    return payload["value"]

                for item in payload.get("nodes", []):
                    try:
                        peer = Peer(
                            node_id=item["node_id"],
                            host=item["host"],
                            port=item["port"]
                        )

                        self.add_peer(peer)

                        if peer.node_id not in queried:
                            candidates.append(peer)

                    except (KeyError, TypeError, ValueError):
                        continue

        return None
