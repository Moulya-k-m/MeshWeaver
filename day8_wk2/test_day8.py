
import time

from node_identity import generate_node_id, calculate_xor_distance
from peer_info import PeerInfo


def test_day8():

    print("MESHWEAVER - DAY 8 INTEGRATION TEST")
    print("-----------------------------------")

    # Generate two node identities
    node_a = generate_node_id()
    node_b = generate_node_id()

    print("\nGenerated Node A:", node_a)
    print("Generated Node B:", node_b)

    # Calculate XOR distance
    distance = calculate_xor_distance(node_a, node_b)

    print("\nXOR Distance:", distance)

    # Create peer information
    peer = PeerInfo(
        node_id=node_b,
        ip_address="127.0.0.1",
        port=9002,
        last_seen=time.time()
    )

    print("\nPeer information:")
    peer.display_info()

    # Update peer activity
    old_timestamp = peer.last_seen
    time.sleep(0.01)
    peer.update_last_seen()

    assert peer.last_seen > old_timestamp

    print("\nPeer timestamp update: PASSED")
    print("Day 8 integration test: PASSED")


if __name__ == "__main__":
    test_day8()
