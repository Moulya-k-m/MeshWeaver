
import sys
from pathlib import Path

sys.path.insert(
    0,
    str(Path(__file__).resolve().parent.parent / "day5_wk1")
)

from worker import execute_task
from serializer import serialize_call


def multiply(a, b):
    return a * b


# Serialize function
encoded = serialize_call(multiply, args=(10, 20))

# Prepare remote task payload
payload = {
    "operation": "REMOTE_CALL",
    "encoded": encoded
}

# Execute through MeshWeaver worker
result = execute_task(payload)

print("Worker execution result:", result)

assert result == 200

print("WORKER TEST PASSED!")
