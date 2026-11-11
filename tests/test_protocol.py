
from meshweaver.protocol import (
    create_message,
    encode_message,
    decode_message,
)


def test_create_message():
    message = create_message("chat", "Moulya", "Hello")

    assert message == {
        "type": "chat",
        "sender": "Moulya",
        "payload": "Hello",
    }


def test_encode_message_adds_newline():
    message = create_message("chat", "Moulya", "Hello")

    encoded = encode_message(message)

    assert encoded.endswith("\n")


def test_decode_message():
    data = '{"type": "chat", "sender": "Moulya", "payload": "Hello"}'

    decoded = decode_message(data)

    assert decoded["type"] == "chat"
    assert decoded["sender"] == "Moulya"
    assert decoded["payload"] == "Hello"


def test_protocol_round_trip():
    message = create_message("chat", "Moulya", "Hello")

    decoded = decode_message(encode_message(message))

    assert decoded == message
