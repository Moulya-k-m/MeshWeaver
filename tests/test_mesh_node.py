import pytest

from meshweaver.node import MeshNode
from meshweaver.peer import Peer
from meshweaver.client import MeshClient
from meshweaver.protocol import create_message


def test_mesh_node_generates_identity():
    node = MeshNode()

    assert isinstance(node.get_node_id(), str)
    assert len(node.get_node_id()) == 32


def test_mesh_nodes_have_unique_identities():
    node1 = MeshNode()
    node2 = MeshNode()

    assert node1.get_node_id() != node2.get_node_id()


def test_mesh_node_custom_identity():
    node = MeshNode(node_id="node-101")

    assert node.get_node_id() == "node-101"


def test_mesh_node_starts_with_empty_peer_registry():
    node = MeshNode()

    assert node.get_peers() == []


def test_mesh_node_adds_peer():
    node = MeshNode()
    peer = Peer("node-2", "127.0.0.1", 8889)

    node.add_peer(peer)

    assert node.get_peers() == [peer]


def test_mesh_node_rejects_duplicate_peer():
    node = MeshNode()
    peer = Peer("node-2", "127.0.0.1", 8889)

    node.add_peer(peer)

    with pytest.raises(ValueError):
        node.add_peer(peer)


def test_mesh_node_rejects_itself_as_peer():
    node = MeshNode(node_id="node-101")
    peer = Peer("node-101", "127.0.0.1", 8888)

    with pytest.raises(ValueError):
        node.add_peer(peer)


def test_mesh_node_uses_configured_host_and_port():
    node = MeshNode(host="127.0.0.1", port=9000)

    assert node.host == "127.0.0.1"
    assert node.port == 9000


import asyncio


def test_mesh_node_starts_and_stops_server():
    async def run():
        node = MeshNode(port=0)

        await node.start()

        assert node.server is not None
        assert node.server.is_serving()

        await node.stop()

        assert node.server is None

    asyncio.run(run())


def test_mesh_node_rejects_double_start():
    async def run():
        node = MeshNode(port=0)

        await node.start()

        try:
            with pytest.raises(RuntimeError):
                await node.start()
        finally:
            await node.stop()

    asyncio.run(run())


def test_mesh_node_can_stop_without_starting():
    async def run():
        node = MeshNode()

        await node.stop()

        assert node.server is None

    asyncio.run(run())


def test_mesh_node_handles_client_task():
    async def run():
        node = MeshNode(node_id="node-101", port=0)
        client = None

        try:
            await node.start()

            actual_port = node.server.sockets[0].getsockname()[1]

            client = MeshClient("127.0.0.1", actual_port)
            await client.connect()

            message = create_message(
                "task",
                "node-202",
                {
                    "operation": "add",
                    "args": [10, 20]
                }
            )

            await client.send(message)
            response = await client.receive()

            assert response["type"] == "result"
            assert response["sender"] == "node-101"
            assert response["payload"]["status"] == "success"
            assert response["payload"]["result"] == 30

        finally:
            if client is not None:
                await client.close()

            await node.stop()

    asyncio.run(run())

