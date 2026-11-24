
import asyncio
import json
import os
import subprocess
import sys
import time
from pathlib import Path

# --------------------------------------------------
# CONFIGURATION
# --------------------------------------------------

ROOT = Path(__file__).resolve().parent
NODE_DIR = ROOT / "day5_wk1"
NODE_SCRIPT = NODE_DIR / "node.py"

TCP_PORTS = list(range(8001, 8011))
DISCOVERY_WAIT = 8
REPORT_FILE = ROOT / "audit_10_nodes_report.json"
LOG_DIR = ROOT / "audit_logs"

# Make Day 5 modules importable from this script.
sys.path.insert(0, str(NODE_DIR))

from framing import read_msg, write_msg
from security import sign, verify


# --------------------------------------------------
# AUTHENTICATED TCP REQUEST
# --------------------------------------------------

async def send_request(port, message):
    reader = None
    writer = None

    try:
        reader, writer = await asyncio.wait_for(
            asyncio.open_connection("127.0.0.1", port),
            timeout=3,
        )

        await asyncio.wait_for(
            write_msg(writer, sign(message)),
            timeout=3,
        )

        response = await asyncio.wait_for(
            read_msg(reader),
            timeout=3,
        )

        if not verify(response):
            raise ConnectionError("Invalid response signature")

        return response

    finally:
        if writer is not None:
            writer.close()
            try:
                await writer.wait_closed()
            except OSError:
                pass


# --------------------------------------------------
# START AND CHECK NODES
# --------------------------------------------------

async def main():

    if not os.environ.get("MESHWEAVER_SECRET"):
        print("ERROR: MESHWEAVER_SECRET is not configured.")
        return

    if not NODE_SCRIPT.exists():
        print("ERROR: Day 5 node.py was not found.")
        return

    LOG_DIR.mkdir(exist_ok=True)

    processes = []
    log_handles = []

    try:
        print("\nStarting 10 MeshWeaver nodes...\n")

        for port in TCP_PORTS:
            log_path = LOG_DIR / f"node_{port}.log"
            log_file = open(log_path, "w", encoding="utf-8")
            log_handles.append(log_file)

            process = subprocess.Popen(
                [
                    sys.executable,
                    str(NODE_SCRIPT),
                    "--tcp",
                    str(port),
                ],
                cwd=str(NODE_DIR),
                stdout=log_file,
                stderr=subprocess.STDOUT,
            )

            processes.append((port, process))
            print(f"Started node on TCP port {port}")

        # Wait until each node responds to HELLO.
        print("\nWaiting for nodes to become ready...")

        node_ids = {}

        for attempt in range(30):
            for port, process in processes:
                if port in node_ids or process.poll() is not None:
                    continue

                try:
                    response = await send_request(
                        port,
                        {"type": "HELLO"},
                    )

                    if response.get("type") == "HELLO_ACK":
                        node_ids[port] = response["node_id"]

                except Exception:
                    pass

            if len(node_ids) == len(TCP_PORTS):
                break

            await asyncio.sleep(0.5)

        print(
            f"\nNodes responding: "
            f"{len(node_ids)}/{len(TCP_PORTS)}"
        )

        if not node_ids:
            print("No nodes became ready. Check audit_logs.")
            return

        # Allow UDP discovery and gossip to run.
        print(f"\nWaiting {DISCOVERY_WAIT} seconds for discovery...")
        await asyncio.sleep(DISCOVERY_WAIT)

        # --------------------------------------------------
        # DISCOVERY AUDIT
        # --------------------------------------------------

        print("\nCollecting peer tables...")

        discovery_results = {}

        for port, node_id in node_ids.items():
            try:
                response = await send_request(
                    port,
                    {"type": "PEERS"},
                )

                peers = response.get("peers", [])

                discovered_ids = {
                    peer.get("node_id")
                    for peer in peers
                    if peer.get("node_id")
                }

                direct = sum(
                    1 for peer in peers
                    if peer.get("direct") is True
                )

                indirect = sum(
                    1 for peer in peers
                    if peer.get("direct") is False
                )

                expected_ids = set(node_ids.values()) - {node_id}
                discovered_expected = (
                    discovered_ids & expected_ids
                )

                discovery_results[str(port)] = {
                    "node_id": node_id,
                    "known_peers": len(discovered_ids),
                    "direct_peers": direct,
                    "indirect_peers": indirect,
                    "expected_peers": len(expected_ids),
                    "discovered_project_nodes": len(
                        discovered_expected
                    ),
                    "missing_peers": sorted(
                        expected_ids - discovered_ids
                    ),
                }

                print(
                    f"Node {port}: "
                    f"{len(discovered_expected)}/"
                    f"{len(expected_ids)} expected peers discovered "
                    f"(direct: {direct}, indirect: {indirect})"
                )

            except Exception as error:
                discovery_results[str(port)] = {
                    "error": str(error)
                }
                print(f"Node {port}: PEERS query failed: {error}")

        # --------------------------------------------------
        # FULL TCP CONNECTIVITY AUDIT
        # --------------------------------------------------

        print("\nTesting authenticated TCP connectivity...")

        tcp_success = 0
        tcp_failed = 0
        tcp_failures = []

        ready_ports = list(node_ids.keys())

        for source_port in ready_ports:
            for target_port in ready_ports:
                if source_port == target_port:
                    continue

                try:
                    response = await send_request(
                        target_port,
                        {"type": "HELLO"},
                    )

                    expected_id = node_ids[target_port]

                    if (
                        response.get("type") == "HELLO_ACK"
                        and response.get("node_id") == expected_id
                    ):
                        tcp_success += 1
                    else:
                        raise ConnectionError(
                            "Unexpected HELLO response"
                        )

                except Exception as error:
                    tcp_failed += 1
                    tcp_failures.append({
                        "source_port": source_port,
                        "target_port": target_port,
                        "error": str(error),
                    })

        # --------------------------------------------------
        # CALCULATE RESULTS
        # --------------------------------------------------

        expected_discovery = (
            len(ready_ports) * max(0, len(ready_ports) - 1)
        )

        actual_discovery = sum(
            result.get("discovered_project_nodes", 0)
            for result in discovery_results.values()
        )

        discovery_percent = (
            actual_discovery / expected_discovery * 100
            if expected_discovery else 0
        )

        tcp_attempted = tcp_success + tcp_failed

        tcp_percent = (
            tcp_success / tcp_attempted * 100
            if tcp_attempted else 0
        )

        report = {
            "audit": "MeshWeaver 10-node network audit",
            "nodes_requested": len(TCP_PORTS),
            "nodes_started": len(ready_ports),
            "node_ports": ready_ports,
            "discovery": {
                "expected_peer_entries": expected_discovery,
                "discovered_peer_entries": actual_discovery,
                "coverage_percent": round(discovery_percent, 2),
                "per_node": discovery_results,
            },
            "authenticated_tcp": {
                "attempted": tcp_attempted,
                "successful": tcp_success,
                "failed": tcp_failed,
                "success_percent": round(tcp_percent, 2),
                "failures": tcp_failures,
            },
        }

        REPORT_FILE.write_text(
            json.dumps(report, indent=4),
            encoding="utf-8",
        )

        # --------------------------------------------------
        # FINAL SUMMARY
        # --------------------------------------------------

        print("\n" + "=" * 48)
        print("       MESHWEAVER NETWORK AUDIT")
        print("=" * 48)

        print(f"Nodes started: {len(ready_ports)}/10")

        print(
            f"Discovery coverage: "
            f"{actual_discovery}/{expected_discovery} "
            f"({discovery_percent:.2f}%)"
        )

        print(
            f"Authenticated TCP: "
            f"{tcp_success}/{tcp_attempted} "
            f"({tcp_percent:.2f}%)"
        )

        print(f"\nReport saved to: {REPORT_FILE}")
        print(f"Node logs saved in: {LOG_DIR}")

        print("=" * 48)

    finally:
        print("\nStopping audit nodes...")

        for port, process in processes:
            if process.poll() is None:
                process.terminate()

        for port, process in processes:
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait()

        for log_file in log_handles:
            log_file.close()

        print("Audit nodes stopped.")


if __name__ == "__main__":
    asyncio.run(main())
