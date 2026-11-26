
import asyncio
import socket

from meshweaver.node import MeshNode


def get_free_port():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind(("127.0.0.1", 0))
        return sock.getsockname()[1]


def test_two_nodes_join_and_discover_each_other():
    async def scenario():
        node_a = MeshNode(port=get_free_port(), node_id="node-A")
        node_b = MeshNode(port=get_free_port(), node_id="node-B")

        try:
            await node_a.start()
            await node_b.start()

            await node_b.join_network(
                "127.0.0.1",
                node_a.port,
                node_a.get_node_id()
            )

            assert node_a.dht.routing_table.find_closest(
                node_b.get_node_id()
            )

            assert node_b.dht.routing_table.find_closest(
                node_a.get_node_id()
            )

        finally:
            await node_a.stop()
            await node_b.stop()

    asyncio.run(scenario())


def test_remote_dht_storage_and_retrieval():
    async def scenario():
        node_a = MeshNode(port=get_free_port(), node_id="storage-A")
        node_b = MeshNode(port=get_free_port(), node_id="storage-B")

        try:
            await node_a.start()
            await node_b.start()

            await node_b.join_network(
                "127.0.0.1",
                node_a.port,
                node_a.get_node_id()
            )

            await node_a.dht.store(
                "meshweaver-test",
                {"message": "Hello from Node A"}
            )

            result = await node_b.dht.find_value("meshweaver-test")

            assert result == {"message": "Hello from Node A"}

        finally:
            await node_a.stop()
            await node_b.stop()

    asyncio.run(scenario())
