
import asyncio

from day9_wk2.routing_table import (
    xor_distance,
    validate_node_id
)

from day11_wk2.find_node import FindNodeClient


class LookupManager:

    def __init__(
        self,
        local_node_id,
        routing_table,
        alpha=3,
        k=20,
        timeout=5
    ):
        self.local_node_id = validate_node_id(local_node_id)
        self.routing_table = routing_table
        self.alpha = alpha
        self.k = k
        self.client = FindNodeClient(timeout=timeout)

    async def lookup(self, target_node_id):

        target_node_id = validate_node_id(target_node_id)

        closest_peers = self.routing_table.get_closest_nodes(
            target_node_id,
            count=self.k
        )

        known_peers = {
            peer.node_id: peer
            for peer in closest_peers
        }

        queried_nodes = set()
        failed_nodes = set()

        while True:

            candidates = [
                peer
                for peer in known_peers.values()
                if peer.node_id not in queried_nodes
            ]

            candidates.sort(
                key=lambda peer: xor_distance(
                    peer.node_id,
                    target_node_id
                )
            )

            candidates = candidates[:self.alpha]

            if not candidates:
                break

            for peer in candidates:
                queried_nodes.add(peer.node_id)

            results = await asyncio.gather(
                *[
                    self.client.find_node(
                        peer.ip,
                        peer.port,
                        target_node_id
                    )
                    for peer in candidates
                ],
                return_exceptions=True
            )

            for peer, result in zip(candidates, results):

                if isinstance(result, Exception):
                    failed_nodes.add(peer.node_id)
                    continue

                if not result:
                    failed_nodes.add(peer.node_id)
                    continue

                for discovered_peer in result:

                    if discovered_peer.node_id == self.local_node_id:
                        continue

                    known_peers[discovered_peer.node_id] = (
                        discovered_peer
                    )

            sorted_peers = sorted(
                known_peers.values(),
                key=lambda peer: xor_distance(
                    peer.node_id,
                    target_node_id
                )
            )

            known_peers = {
                peer.node_id: peer
                for peer in sorted_peers[:self.k]
            }

        final_peers = sorted(
            known_peers.values(),
            key=lambda peer: xor_distance(
                peer.node_id,
                target_node_id
            )
        )

        return [
            peer
            for peer in final_peers
            if peer.node_id not in failed_nodes
        ]
