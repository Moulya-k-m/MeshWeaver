
from meshweaver.identity import NodeIdentity


def test_node_identity_generation():
    node = NodeIdentity()

    assert isinstance(node.get_id(), str)
    assert len(node.get_id()) == 32


def test_node_identity_uniqueness():
    node1 = NodeIdentity()
    node2 = NodeIdentity()

    assert node1.get_id() != node2.get_id()


def test_node_identity_custom_id():
    node = NodeIdentity("node-101")

    assert node.get_id() == "node-101"


def test_node_identity_string_representation():
    node = NodeIdentity("node-101")

    assert str(node) == "node-101"
