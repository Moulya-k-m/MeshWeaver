
import asyncio
import streamlit as st

from framing import read_msg, write_msg
from security import sign, verify


NODES = {
    "NODE_A": 8001,
    "NODE_B": 8002,
    "NODE_C": 8003,
}


async def ask(port, request):
    reader = None
    writer = None

    try:
        reader, writer = await asyncio.wait_for(
            asyncio.open_connection("127.0.0.1", port),
            timeout=3
        )

        await write_msg(writer, sign(request))

        response = await asyncio.wait_for(
            read_msg(reader),
            timeout=3
        )

        if not verify(response):
            raise ValueError("Response authentication failed")

        return response

    except Exception as error:
        return {"error": str(error)}

    finally:
        if writer:
            writer.close()
            try:
                await writer.wait_closed()
            except Exception:
                pass


async def collect_data():
    results = {}

    for node_id, port in NODES.items():
        status, peers = await asyncio.gather(
            ask(port, {"type": "STATUS"}),
            ask(port, {"type": "PEERS"})
        )

        results[node_id] = {
            "port": port,
            "status": status,
            "peers": peers
        }

    return results


st.set_page_config(
    page_title="MeshWeaver Dashboard",
    page_icon="🌐",
    layout="wide"
)

st.title("🌐 MeshWeaver")
st.subheader("Decentralized P2P Task Broker")
st.caption("Live monitoring of nodes, resources and task queues.")

if st.button("🔄 Refresh Dashboard"):
    st.rerun()

data = asyncio.run(collect_data())

online = sum(
    1 for item in data.values()
    if "error" not in item["status"]
)

col1, col2, col3 = st.columns(3)

col1.metric("Total Nodes", len(NODES))
col2.metric("Online Nodes", online)
col3.metric("Offline Nodes", len(NODES) - online)

st.divider()
st.header("🖥️ Node Monitoring")

columns = st.columns(3)

for column, (node_id, item) in zip(columns, data.items()):

    with column:
        st.subheader(node_id)
        st.caption(f"TCP Port: {item['port']}")

        status = item["status"]

        if "error" in status:
            st.error("OFFLINE")
            st.caption(status["error"])
            continue

        st.success("ONLINE")

        load = status.get("load", {})
        queue = status.get("queue", {})

        st.metric(
            "CPU Usage",
            f"{load.get('cpu', 0):.1f}%"
        )

        st.progress(
            min(100, max(0, int(load.get("cpu", 0))))
        )

        st.metric(
            "RAM Usage",
            f"{load.get('ram', 0):.1f}%"
        )

        st.progress(
            min(100, max(0, int(load.get("ram", 0))))
        )

        st.metric(
            "Active Tasks",
            load.get("active_tasks", 0)
        )

        st.metric(
            "Connected Peers",
            status.get("peer_count", 0)
        )

        with st.expander("Task Queue Details"):
            st.json(queue)

        with st.expander("Peer Information"):
            peers_response = item["peers"]

            if "error" in peers_response:
                st.warning("Could not retrieve peer information.")
            else:
                peers = peers_response.get("peers", [])

                if peers:
                    for peer in peers:
                        st.write(
                            f"**{peer.get('node_id', 'Unknown')}** — "
                            f"{peer.get('state', 'Unknown')}"
                        )
                else:
                    st.info("No peers discovered yet.")

st.divider()
st.subheader("📊 Network Summary")

for node_id, item in data.items():
    status = item["status"]

    if "error" not in status:
        queue = status.get("queue", {})

        st.write(
            f"**{node_id}** — "
            f"Pending: {queue.get('PENDING', 0)} | "
            f"Running: {queue.get('RUNNING', 0)} | "
            f"Completed: {queue.get('COMPLETED', 0)} | "
            f"Failed: {queue.get('FAILED', 0)}"
        )

st.divider()
st.caption("MeshWeaver | Built with Python, AsyncIO and Streamlit")

