
import asyncio
import os
import re
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent
NODE_FILE = ROOT / "day5_wk1" / "node.py"

sys.path.insert(0, str(ROOT / "day5_wk1"))
sys.path.insert(0, str(ROOT / "day7_wk1"))

from framing import read_msg, write_msg
from security import sign, verify
from serializer import serialize_call


def regression_workload(features, targets, epochs, learning_rate, alpha):
    """Train a small linear regression model on the remote node."""

    import os

    sample_count = len(features)
    feature_count = len(features[0])

    weights = [0.0] * feature_count
    bias = 0.0

    for _ in range(epochs):
        gradients = [0.0] * feature_count
        bias_gradient = 0.0

        for row, target in zip(features, targets):
            prediction = bias + sum(
                weights[j] * row[j]
                for j in range(feature_count)
            )

            error = prediction - target
            bias_gradient += error

            for j in range(feature_count):
                gradients[j] += error * row[j]

        for j in range(feature_count):
            gradient = (
                2 * gradients[j] / sample_count
                + 2 * alpha * weights[j]
            )
            weights[j] -= learning_rate * gradient

        bias -= learning_rate * 2 * bias_gradient / sample_count

    squared_error = 0.0

    for row, target in zip(features, targets):
        prediction = bias + sum(
            weights[j] * row[j]
            for j in range(feature_count)
        )
        squared_error += (prediction - target) ** 2

    return {
        "worker_pid": os.getpid(),
        "weights": weights,
        "bias": bias,
        "mse": squared_error / sample_count,
        "samples": sample_count,
        "epochs": epochs,
    }


async def send_request(port, message):
    reader, writer = await asyncio.wait_for(
        asyncio.open_connection("127.0.0.1", port),
        timeout=4,
    )

    try:
        await write_msg(writer, sign(message))

        response = await asyncio.wait_for(
            read_msg(reader),
            timeout=5,
        )

        if not verify(response):
            raise ConnectionError("Invalid response signature")

        return response

    finally:
        writer.close()
        await writer.wait_closed()


def start_node(port, log_file):
    return subprocess.Popen(
        [
            sys.executable,
            str(NODE_FILE),
            "--tcp",
            str(port),
        ],
        cwd=ROOT,
        env=os.environ.copy(),
        stdout=log_file,
        stderr=subprocess.STDOUT,
    )


async def wait_until_ready(port, process):
    for _ in range(30):
        if process.poll() is not None:
            raise RuntimeError(
                f"Node on port {port} stopped unexpectedly"
            )

        try:
            response = await send_request(
                port,
                {"type": "HELLO"},
            )

            if response.get("type") == "HELLO_ACK":
                return response["node_id"]

        except Exception:
            await asyncio.sleep(0.5)

    raise TimeoutError(f"Node on port {port} did not become ready")


def read_node_pid(log_path, node_id):
    """Read the actual Python process PID from the node startup log."""

    log_text = log_path.read_text(
        encoding="utf-8",
        errors="replace",
    )

    short_id = node_id[:8]

    pattern = (
        rf"Node {re.escape(short_id)} started"
        rf".*?PID:\s*(\d+)"
    )

    match = re.search(pattern, log_text)

    if not match:
        raise RuntimeError(
            f"Could not find startup PID for node {short_id} "
            f"in {log_path.name}"
        )

    return int(match.group(1))


async def main():
    if not os.environ.get("MESHWEAVER_SECRET"):
        raise RuntimeError(
            "MESHWEAVER_SECRET is not set in this terminal"
        )

    processes = {}
    log_handles = {}

    node_a_log = ROOT / "audit_node_8001.log"
    node_b_log = ROOT / "audit_node_8002.log"

    try:
        print("\n=== SERIALIZATION AUDIT ===")

        # STEP 1: Start Node A.
        print("\nSTEP 1: Starting Node A...")

        log_handles[8001] = open(node_a_log, "w")

        processes[8001] = start_node(
            8001,
            log_handles[8001],
        )

        node_a_id = await wait_until_ready(
            8001,
            processes[8001],
        )

        print("Node A ready:", node_a_id[:8])

        # STEP 2: Start Node B.
        print("\nSTEP 2: Starting Node B...")

        log_handles[8002] = open(node_b_log, "w")

        processes[8002] = start_node(
            8002,
            log_handles[8002],
        )

        node_b_id = await wait_until_ready(
            8002,
            processes[8002],
        )

        print("Node B ready:", node_b_id[:8])

        # STEP 3: Wait for discovery.
        print("\nSTEP 3: Waiting for peer discovery...")

        discovered = False

        for _ in range(40):
            response = await send_request(
                8001,
                {"type": "PEERS"},
            )

            peers = response.get("peers", [])

            if any(
                peer.get("node_id") == node_b_id
                for peer in peers
            ):
                discovered = True
                break

            await asyncio.sleep(0.5)

        assert discovered, "Node A could not discover Node B"

        print("PASS: Node A discovered Node B")

        # STEP 4: Make Node B the preferred peer.
        print("\nSTEP 4: Preparing deterministic task routing...")

        report = {
            "type": "LOAD_REPORT",
            "node_id": node_b_id,
            "timestamp": time.time(),
            "snapshot": {
                "cpu": 0.0,
                "ram": 0.0,
                "active_tasks": 0,
            },
        }

        report_response = await send_request(
            8001,
            report,
        )

        assert report_response.get("type") == "LOAD_REPORT_ACK", (
            f"Load report rejected: {report_response}"
        )

        print("PASS: Controlled low-load report accepted")

        # STEP 5: Prepare regression workload.
        print("\nSTEP 5: Preparing ML workload...")

        features = [
            [
                i / 119,
                ((i * 7) % 31) / 30,
                ((i * 13) % 17) / 16,
            ]
            for i in range(120)
        ]

        targets = [
            2.5 * row[0]
            - 1.2 * row[1]
            + 0.7 * row[2]
            + 0.4
            for row in features
        ]

        encoded = serialize_call(
            regression_workload,
            args=(features, targets, 800, 0.08, 0.001),
        )

        print("PASS: Regression function serialized")
        print("Serialized payload:", len(encoded), "characters")

        # STEP 6: Submit through Node A.
        print("\nSTEP 6: Submitting task through Node A...")

        accepted = await send_request(
            8001,
            {
                "type": "SUBMIT_TASK",
                "payload": {
                    "operation": "REMOTE_CALL",
                    "encoded": encoded,
                },
            },
        )

        assert accepted.get("type") == "TASK_ACCEPTED", accepted

        assert accepted.get("forwarded") is True, (
            f"Task was not forwarded: {accepted}"
        )

        assert accepted.get("node_id") == node_b_id, (
            "Task was forwarded to an unexpected node"
        )

        task_id = accepted["task_id"]

        print("PASS: Task forwarded to Node B")
        print("Task ID:", task_id)

        # STEP 7: Retrieve the result through Node A.
        print("\nSTEP 7: Waiting for remote execution...")

        result_response = None

        for _ in range(60):
            result_response = await send_request(
                8001,
                {
                    "type": "GET_RESULT",
                    "task_id": task_id,
                },
            )

            if result_response.get("status") == "COMPLETED":
                break

            if result_response.get("status") == "FAILED":
                raise RuntimeError(
                    "Remote task failed: "
                    f"{result_response.get('error')}"
                )

            await asyncio.sleep(0.5)

        assert result_response.get("status") == "COMPLETED", (
            f"Task did not complete: {result_response}"
        )

        result = result_response["result"]["value"]

        # STEP 8: Verify execution on Node B.
        print("\nSTEP 8: Verifying remote execution...")

        worker_pid = result["worker_pid"]

        # Read the actual Python PID from Node B's startup log.
        expected_pid = read_node_pid(
            node_b_log,
            node_b_id,
        )

        assert worker_pid == expected_pid, (
            f"Execution PID mismatch: worker={worker_pid}, "
            f"Node B={expected_pid}"
        )

        assert result["samples"] == 120
        assert result["epochs"] == 800
        assert result["mse"] < 0.001

        print("PASS: Worker PID matches Node B startup PID")
        print("Node B PID:", expected_pid)
        print("Worker PID:", worker_pid)
        print("Model weights:", result["weights"])
        print("Model bias:", result["bias"])
        print("Mean squared error:", result["mse"])

        print("\n================================")
        print("SERIALIZATION AUDIT PASSED!")
        print("Remote function execution verified.")
        print("================================")

    finally:
        print("\nStopping audit nodes...")

        for process in processes.values():
            if process.poll() is None:
                process.terminate()

        for process in processes.values():
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait()

        for handle in log_handles.values():
            handle.close()

        print("Audit nodes stopped.")


if __name__ == "__main__":
    asyncio.run(main())

