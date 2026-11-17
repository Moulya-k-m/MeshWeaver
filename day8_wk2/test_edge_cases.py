
from node_identity import (
    generate_node_id,
    validate_node_id,
    calculate_xor_distance
)

from peer_info import PeerInfo
import time


def test_edge_cases():

    print("DAY 8 - EDGE CASE TESTING")
    print("-------------------------")

    # Test 1: Generated ID is valid
    node_id = generate_node_id()
    assert validate_node_id(node_id)
    print("Test 1 - Valid Node ID: PASSED")

    # Test 2: Invalid ID length
    assert not validate_node_id("12345")
    print("Test 2 - Invalid ID length: PASSED")

    # Test 3: Invalid hexadecimal ID
    invalid_id = "z" * 40
    assert not validate_node_id(invalid_id)
    print("Test 3 - Invalid hexadecimal ID: PASSED")

    # Test 4: XOR distance of identical IDs
    assert calculate_xor_distance(node_id, node_id) == 0
    print("Test 4 - Identical ID distance: PASSED")

    # Test 5: Invalid ID in XOR calculation
    try:
        calculate_xor_distance("invalid", node_id)
        assert False, "Expected ValueError"
    except ValueError:
        print("Test 5 - Invalid XOR input: PASSED")

    # Test 6: Invalid peer port
    try:
        PeerInfo(
            node_id=node_id,
            ip_address="127.0.0.1",
            port=70000,
            last_seen=time.time()
        )
        assert False, "Expected ValueError"
    except ValueError:
        print("Test 6 - Invalid peer port: PASSED")

    # Test 7: XOR distance symmetry
    node_a = generate_node_id()
    node_b = generate_node_id()

    distance_ab = calculate_xor_distance(node_a, node_b)
    distance_ba = calculate_xor_distance(node_b, node_a)

    assert distance_ab == distance_ba
    print("Test 7 - XOR symmetry: PASSED")

    # Test 8: XOR distance is non-negative
    assert distance_ab >= 0
    print("Test 8 - Non-negative XOR distance: PASSED")

    # Test 9: Different IDs have non-zero distance
    assert distance_ab != 0
    print("Test 9 - Different IDs have non-zero distance: PASSED")

    print("\nAll 9 edge-case tests passed!")


if __name__ == "__main__":
    test_edge_cases()
