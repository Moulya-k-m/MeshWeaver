
import json
import time

from peer_info import PeerInfo
from node_identity import generate_node_id


def test_serialization():

    original_peer = PeerInfo(
        node_id=generate_node_id(),
        ip_address="127.0.0.1",
        port=9001,
        last_seen=time.time()
    )

    # Convert peer object into dictionary
    peer_data = original_peer.to_dict()

    # Convert dictionary into JSON
    json_data = json.dumps(peer_data)

    print("Serialized Peer Information:")
    print(json_data)

    # Convert JSON back into dictionary
    received_data = json.loads(json_data)

    # Reconstruct original peer object
    restored_peer = PeerInfo.from_dict(received_data)

    # Compare original and restored information
    assert original_peer == restored_peer

    print("\nSerialization test: PASSED")
    print("Deserialization test: PASSED")
    print("Peer information preserved successfully!")


if __name__ == "__main__":
    test_serialization()
