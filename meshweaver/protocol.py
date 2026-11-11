
from meshweaver.serialization import serialize, deserialize


def create_message(message_type, sender, payload):
    """Create a standardized MeshWeaver message."""
    return {
        "type": message_type,
        "sender": sender,
        "payload": payload
    }


def encode_message(message):
    """Serialize a message and add newline framing."""
    return serialize(message) + "\n"


def decode_message(data):
    """Decode a received JSON message."""
    return deserialize(data)
