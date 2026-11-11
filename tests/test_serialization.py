
import pytest

from meshweaver.serialization import serialize, deserialize


def test_serialize_dictionary():
    message = {"type": "chat", "sender": "Moulya", "payload": "Hello"}
    result = serialize(message)

    assert isinstance(result, str)


def test_deserialize_json():
    data = '{"type": "chat", "sender": "Moulya", "payload": "Hello"}'
    result = deserialize(data)

    assert result["sender"] == "Moulya"
    assert result["payload"] == "Hello"


def test_round_trip():
    message = {"type": "chat", "sender": "Moulya", "payload": "Hello"}
    assert deserialize(serialize(message)) == message


def test_invalid_json():
    with pytest.raises(ValueError):
        deserialize("{invalid json}")
