
import hashlib
import hmac
import json
import os
import time

MAX_AGE = 10.0

SECRET = os.environ.get("MESHWEAVER_SECRET", "").encode()

if not SECRET:
    raise RuntimeError(
        "MESHWEAVER_SECRET environment variable is not set."
    )


def _mac(msg: dict) -> str:
    body = json.dumps(
        msg,
        sort_keys=True,
        separators=(",", ":")
    ).encode()

    return hmac.new(
        SECRET,
        body,
        hashlib.sha256
    ).hexdigest()


def sign(msg: dict) -> dict:
    """Sign a copy of a message with timestamp and HMAC."""

    out = dict(msg)
    out["ts"] = time.time()
    out["sig"] = _mac(out)

    return out


def verify(msg) -> bool:
    """Verify message signature and timestamp."""

    if not isinstance(msg, dict):
        return False

    if "sig" not in msg or "ts" not in msg:
        return False

    sig = msg["sig"]

    if not isinstance(sig, str):
        return False

    body = {
        key: value
        for key, value in msg.items()
        if key != "sig"
    }

    expected = _mac(body)

    if not hmac.compare_digest(sig, expected):
        return False

    try:
        timestamp = float(msg["ts"])

        if not (float("-inf") < timestamp < float("inf")):
            return False

        return abs(time.time() - timestamp) <= MAX_AGE

    except (TypeError, ValueError):
        return False
