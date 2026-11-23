import uuid


class NodeIdentity:
    """Represents the unique identity of a MeshWeaver node."""

    def __init__(self, node_id=None):
        self.node_id = node_id or uuid.uuid4().hex

    def get_id(self):
        """Return the node's unique identifier."""
        return self.node_id

    def __str__(self):
        return self.node_id
