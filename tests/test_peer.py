
import pytest

from meshweaver.peer import Peer, PeerRegistry


def test_peer_creation():
    peer = Peer("node-1", "127.0.0.1", 8888)

    assert peer.node_id == "node-1"
    assert peer.host == "127.0.0.1"
    assert peer.port == 8888


def test_peer_registry_add():
    registry = PeerRegistry()
    peer = Peer("node-1", "127.0.0.1", 8888)

    registry.add_peer(peer)

    assert len(registry) == 1


def test_peer_registry_get():
    registry = PeerRegistry()
    peer = Peer("node-1", "127.0.0.1", 8888)

    registry.add_peer(peer)

    assert registry.get_peer("node-1") == peer


def test_peer_registry_duplicate():
    registry = PeerRegistry()
    peer = Peer("node-1", "127.0.0.1", 8888)

    registry.add_peer(peer)

    with pytest.raises(ValueError):
        registry.add_peer(peer)


def test_peer_registry_remove():
    registry = PeerRegistry()
    peer = Peer("node-1", "127.0.0.1", 8888)

    registry.add_peer(peer)

    assert registry.remove_peer("node-1") is True
    assert len(registry) == 0


def test_peer_registry_get_all():
    registry = PeerRegistry()

    peer1 = Peer("node-1", "127.0.0.1", 8888)
    peer2 = Peer("node-2", "127.0.0.1", 8889)

    registry.add_peer(peer1)
    registry.add_peer(peer2)

    assert len(registry.get_all_peers()) == 2


def test_invalid_peer_port():
    with pytest.raises(ValueError):
        Peer("node-1", "127.0.0.1", 70000)


def test_invalid_peer_host():
    with pytest.raises(ValueError):
        Peer("node-1", "", 8888)
