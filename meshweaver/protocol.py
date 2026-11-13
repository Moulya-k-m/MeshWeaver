
import uuid

from meshweaver.serialization import serialize, deserialize


def create_message(message_type, sender, payload):
    """Create a standardized MeshWeaver message."""
    return {
        "type": message_type,
        "id": uuid.uuid4().hex,
        "sender": sender,
        "payload": payload
    }


def encode_message(message):
    """Serialize a message and add newline framing."""
    return serialize(message) + "\n"

def decode_message(data):
    """Decode and validate a received JSON message."""
    message = deserialize(data)
    validate_message(message)
    return message

def validate_message(message):
    """Validate the structure of a MeshWeaver message."""
    if not isinstance(message, dict):
        raise ValueError("Message must be a dictionary")

    required_fields = ["type", "id", "sender", "payload"]

    for field in required_fields:
        if field not in message:
            raise ValueError(f"Missing required field: {field}")

    for field in ["type", "id", "sender"]:
        if not isinstance(message[field], str) or not message[field]:
            raise ValueError(f"{field} must be a non-empty string")

    return True
