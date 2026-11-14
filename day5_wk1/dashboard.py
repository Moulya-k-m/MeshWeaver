
import argparse
import asyncio
import os

from framing import read_msg, write_msg
from security import sign, verify

os.system("")

GREEN, YELLOW, RED, CYAN, DIM, RESET = (
    "\033[92m", "\033[93m", "\033[91m",
    "\033[96m", "\033[2m", "\033[0m"
)

STATE_COLOR = {
    "ALIVE": GREEN,
    "SUSPECT": YELLOW,
    "DEAD": RED,
    "LEFT": RED
}


async def ask(port, req, timeout=2.0):
    """Send a signed request and verify the signed response."""

    async def call():
        reader, writer = await asyncio.open_connection(
            "127.0.0.1", port
        )

        try:
            await write_msg(writer, sign(req))
            response = await read_msg(reader)

            if not verify(response):
                raise ValueError("Invalid response signature")

            return response

        finally:
            writer.close()
            await writer.wait_closed()

    try:
        return await asyncio.wait_for(call(), timeout)

    except (
        OSError,
        asyncio.TimeoutError,
        asyncio.IncompleteReadError,
        ValueError
    ):
        return None


def bar(percent, width=12):
    percent = max(0, min(100, percent or 0))
    filled = round(width * percent / 100)

    color = (
        GREEN if percent < 60
        else YELLOW if percent < 85
        else RED
    )

    return (
        f"{color}{'█' * filled}"
        f"{DIM}{'░' * (width - filled)}"
        f"{RESET} {percent:5.1f}%"
    )


async def render(ports):

    statuses = await asyncio.gather(
        *(ask(p, {"type": "STATUS"}) for p in ports)
    )

    lines = [
        f"{CYAN}MeshWeaver Live Dashboard{RESET}  (Ctrl+C to quit)",
        ""
    ]

    lines.append(
        f"{'PORT':<6}{'NODE':<10}{'STATE':<9}"
        f"{'CPU':<22}{'RAM':<22}"
        f"{'ACTIVE':<8}{'PEND':<6}"
        f"{'RUN':<5}{'DONE':<6}FAIL"
    )

    for port, s in zip(ports, statuses):

        if s is None:
            lines.append(
                f"{port:<6}{'-':<10}{RED}{'DOWN':<9}{RESET}"
            )
            continue

        load = s.get("load", {})
        queue = s.get("queue", {})

        lines.append(
            f"{port:<6}{s['node_id'][:8]:<10}"
            f"{GREEN}{'UP':<9}{RESET}"
            f"{bar(load.get('cpu')):<31}"
            f"{bar(load.get('ram')):<31}"
            f"{load.get('active_tasks', 0):<8}"
            f"{queue.get('PENDING', 0):<6}"
            f"{queue.get('RUNNING', 0):<5}"
            f"{queue.get('COMPLETED', 0):<6}"
            f"{queue.get('FAILED', 0)}"
        )

    # Display peers from the first available node
    for port, s in zip(ports, statuses):

        if s is None:
            continue

        response = await ask(port, {"type": "PEERS"})

        if response and response.get("peers"):

            lines += [
                "",
                f"{CYAN}Peers as seen by "
                f"{s['node_id'][:8]}:{RESET}"
            ]

            for peer in response["peers"]:
                state = peer.get("state", "?")

                lines.append(
                    f"  {peer['node_id'][:8]:<10}"
                    f"{STATE_COLOR.get(state, RESET)}"
                    f"{state}{RESET}"
                )

        break

    return "\n".join(lines)


async def main(ports, interval):

    while True:
        frame = await render(ports)

        print("\033[2J\033[H" + frame, flush=True)

        await asyncio.sleep(interval)


if __name__ == "__main__":

    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--ports",
        type=int,
        nargs="+",
        default=[8001, 8002, 8003]
    )

    parser.add_argument(
        "--interval",
        type=float,
        default=1.0
    )

    args = parser.parse_args()

    try:
        asyncio.run(main(args.ports, args.interval))

    except KeyboardInterrupt:
        print("\nDashboard stopped.")
