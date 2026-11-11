import json


def serialize(message):
    """Convert a Python dictionary into a JSON string."""
    return json.dumps(message)


def deserialize(data):
    """Convert a JSON string into a Python dictionary."""
    return json.loads(data)
