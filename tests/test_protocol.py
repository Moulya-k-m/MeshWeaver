
import pytest

from meshweaver.protocol import (
    create_message,
    encode_message,
    decode_message,
    validate_message,
)


def test_create_message():
    message = create_message("chat", "Moulya", "Hello")

    assert message["type"] == "chat"
    assert message["sender"] == "Moulya"
    assert message["payload"] == "Hello"
    assert "id" in message
    assert len(message["id"]) == 32


def test_encode_message_adds_newline():
    message = create_message("chat", "Moulya", "Hello")

    encoded = encode_message(message)

    assert encoded.endswith("\n")


def test_decode_message():
    message = create_message("chat", "Moulya", "Hello")
    decoded = decode_message(encode_message(message))

    assert decoded["type"] == "chat"
    assert decoded["sender"] == "Moulya"
    assert decoded["payload"] == "Hello"


def test_protocol_round_trip():
    message = create_message("chat", "Moulya", "Hello")

    decoded = decode_message(encode_message(message))

    assert decoded == message


def test_messages_have_unique_ids():
    message1 = create_message("chat", "Moulya", "Hello")
    message2 = create_message("chat", "Moulya", "World")

    assert message1["id"] != message2["id"]


def test_validate_valid_message():
    message = create_message("chat", "Moulya", "Hello")

    assert validate_message(message) is True


def test_validate_missing_field():
    message = {
        "type": "chat",
        "id": "123",
        "sender": "Moulya"
    }

    with pytest.raises(ValueError):
        validate_message(message)


def test_validate_invalid_type():
    message = {
        "type": "",
        "id": "123",
        "sender": "Moulya",
        "payload": "Hello"
    }

    with pytest.raises(ValueError):
        validate_message(message)


def test_decode_rejects_invalid_message():
    data = '{"type": "chat", "sender": "Moulya"}'

    with pytest.raises(ValueError):
        decode_message(data)
