
import secrets


# Kademlia uses 160-bit node IDs
ID_BITS = 160
ID_BYTES = ID_BITS // 8


def generate_node_id():
    """
    Generate a unique 160-bit node ID.
    Returns a 40-character hexadecimal string.
    """
    node_id = secrets.token_hex(ID_BYTES)
    return node_id


def validate_node_id(node_id):
    """
    Validate a 160-bit hexadecimal node ID.
    """
    if not isinstance(node_id, str):
        return False

    if len(node_id) != 40:
        return False

    try:
        int(node_id, 16)
        return True
    except ValueError:
        return False


def calculate_xor_distance(node_id_1, node_id_2):
    """
    Calculate XOR distance between two node IDs.
    """
    if not validate_node_id(node_id_1):
        raise ValueError("Invalid first node ID")

    if not validate_node_id(node_id_2):
        raise ValueError("Invalid second node ID")

    id_1 = int(node_id_1, 16)
    id_2 = int(node_id_2, 16)

    distance = id_1 ^ id_2

    return distance


if __name__ == "__main__":

    # Generate a random node identity
    node_id = generate_node_id()

    print("MeshWeaver Node Identity")
    print("------------------------")
    print("Node ID:", node_id)
    print("ID Length:", len(node_id))
    print("Valid ID:", validate_node_id(node_id))

    # Test XOR distance calculation
    node_a = "000000000000000000000000000000000000000a"
    node_b = "000000000000000000000000000000000000000c"

    distance = calculate_xor_distance(node_a, node_b)

    print("\nXOR Distance Test")
    print("-----------------")
    print("Node A:", node_a)
    print("Node B:", node_b)
    print("Distance:", distance)
