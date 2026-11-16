
import base64
import cloudpickle

MAX_SERIALIZED_SIZE = 700_000


def serialize_call(function, args=(), kwargs=None):

    if not callable(function):
        raise TypeError("Expected a callable function")

    if kwargs is None:
        kwargs = {}

    if not isinstance(args, tuple):
        raise TypeError("Arguments must be a tuple")

    if not isinstance(kwargs, dict):
        raise TypeError("Keyword arguments must be a dictionary")

    call_data = {
        "function": function,
        "args": args,
        "kwargs": kwargs
    }

    serialized = cloudpickle.dumps(call_data)

    if len(serialized) > MAX_SERIALIZED_SIZE:
        raise ValueError("Serialized function is too large")

    encoded = base64.b64encode(serialized).decode("ascii")

    return encoded


def deserialize_call(encoded):

    if not isinstance(encoded, str):
        raise TypeError("Encoded data must be a string")

    try:
        serialized = base64.b64decode(encoded, validate=True)
    except Exception as exc:
        raise ValueError("Invalid Base64 data") from exc

    if len(serialized) > MAX_SERIALIZED_SIZE:
        raise ValueError("Serialized function is too large")

    call_data = cloudpickle.loads(serialized)

    if not isinstance(call_data, dict):
        raise ValueError("Invalid function package")

    function = call_data.get("function")
    args = call_data.get("args")
    kwargs = call_data.get("kwargs")

    if not callable(function):
        raise ValueError("Invalid function")

    if not isinstance(args, tuple) or not isinstance(kwargs, dict):
        raise ValueError("Invalid arguments")

    return function, args, kwargs

