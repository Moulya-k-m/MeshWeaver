# Day 5 – Persistent Task Recovery, Message Authentication, Peer Gossip and Monitoring Dashboards

## Overview

Day 5 focuses on improving the reliability, security, peer discovery and observability of MeshWeaver.

It introduces persistent task journaling, recovery of unfinished tasks after node restarts, HMAC-SHA256 message authentication, indirect peer discovery through gossip and live monitoring dashboards.

These enhancements help MeshWeaver maintain task information across restarts, validate communication between nodes, discover peers through existing network members and monitor the overall cluster status.

## Project Files

| File | Purpose |
|---|---|
| `journal.py` | Maintains an append-only JSON Lines journal of task state changes |
| `task_store.py` | Integrates persistent journaling with task management and recovery |
| `security.py` | Implements HMAC-SHA256 message signing and verification |
| `discovery.py` | Handles UDP peer announcements and indirect peer-list exchange |
| `peer_table.py` | Maintains direct and indirectly discovered peer information |
| `node.py` | Integrates persistent storage, message authentication, peer discovery and task processing |
| `dashboard.py` | Provides a terminal-based live cluster monitoring dashboard |
| `web_dashboard.py` | Provides a browser-based monitoring dashboard using Streamlit |
| `framing.py` | Reuses Day 3 length-prefixed JSON TCP message framing |
| `resource_gossip.py` | Continues exchanging authenticated resource reports between active peers |

## Features Implemented

### 1. Persistent Task Journaling

Implemented an append-only task journal using JSON Lines (JSONL) format.

The journal records task state changes so that task information can be restored when a node restarts.

Features include:

- Stores task information in a persistent JSONL file.
- Records task state changes as separate journal entries.
- Replays journal entries during initialization.
- Restores previously recorded task information.
- Identifies unfinished tasks during recovery.
- Requeues tasks that were in the RUNNING state as PENDING.

This helps prevent unfinished tasks from being permanently lost when a node restarts.

### 2. Task Recovery After Restart

Integrated persistent journaling with the asynchronous task store.

During node initialization:

- Previously recorded tasks are loaded from the journal.
- Task states are reconstructed.
- Tasks that were RUNNING before shutdown are returned to the PENDING queue.
- Recovered tasks can be processed by the worker again.

Task recovery behavior:

`RUNNING → PENDING → RUNNING → COMPLETED`

This improves task reliability by allowing unfinished tasks to be retried after a node restart.

### 3. HMAC-SHA256 Message Authentication

Implemented message authentication using the HMAC-SHA256 algorithm.

This helps nodes verify that received messages were generated using the shared secret.

Features include:

- Generates HMAC-SHA256 signatures for messages.
- Adds timestamps to signed messages.
- Verifies message signatures before processing requests.
- Rejects messages with invalid or modified signatures.
- Checks message timestamp freshness.
- Uses an environment variable to configure the shared secret.

The shared secret is configured using:

`MESHWEAVER_SECRET`

This authentication mechanism is integrated into TCP communication, resource gossip and UDP discovery.

It helps protect communication against message tampering and unauthorized messages without transmitting the shared secret itself.

### 4. Authenticated Node Communication

Integrated message signing and verification into node-to-node communication.

- Outgoing TCP requests are signed before transmission.
- Incoming requests are verified before processing.
- Responses are signed by the receiving node.
- Responses are verified by the requesting node.
- Invalid messages are rejected.
- Authenticated resource reports are exchanged between peers.

This ensures that the main communication paths use message authentication.

### 5. Indirect Peer Discovery Through Gossip

Enhanced the UDP discovery mechanism to support peer-list exchange.

Previously, nodes primarily discovered one another through configured UDP seed ports.

The updated implementation allows nodes to share information about peers they already know.

Features include:

- Nodes periodically broadcast authenticated UDP announcements.
- Announcements contain the sender's node ID and TCP port.
- Announcements also include a list of known peers.
- Nodes learn about other peers through announcements received from existing peers.
- Indirectly discovered peers are stored separately from directly discovered peers.
- Invalid peer information is ignored.
- Peer-list exchange is limited to a maximum of 50 entries per announcement.

This improves network discovery by allowing nodes to learn about other nodes without receiving their direct announcements.

### 6. Direct and Indirect Peer Management

Enhanced the peer table to distinguish between directly discovered and indirectly discovered nodes.

Each peer maintains information such as:

- Node ID
- Host address
- TCP port
- Last-seen timestamp
- Peer state
- Direct discovery status

Peer states include:

| State | Description |
|---|---|
| `ALIVE` | Directly discovered and recently active peer |
| `SUSPECT` | Direct peer has not been heard from within the configured threshold |
| `DEAD` | Direct peer has exceeded the failure timeout |
| `UNKNOWN` | Indirectly discovered peer that has not yet been directly confirmed |

Indirectly discovered peers are not automatically treated as active peers for scheduling or resource gossip.

This helps prevent unverified peer information from being treated as an established active connection.

### 7. Terminal Monitoring Dashboard

Implemented a terminal-based dashboard to monitor the status of multiple MeshWeaver nodes.

The dashboard provides:

- Node availability status.
- TCP connection status.
- CPU utilization.
- RAM utilization.
- Active task information.
- Task queue statistics.
- Peer information and peer states.
- Periodic status updates.

The dashboard communicates with nodes using authenticated TCP requests.

It refreshes the displayed cluster information approximately every second.

### 8. Web-Based Monitoring Dashboard

Implemented a browser-based monitoring dashboard using Streamlit.

The dashboard provides a visual overview of the MeshWeaver cluster.

Features include:

- Total number of configured nodes.
- Number of online and offline nodes.
- CPU utilization for each node.
- RAM utilization for each node.
- Active task counts.
- Peer counts.
- Task queue statistics.
- Individual node status information.
- Peer information and network overview.

The dashboard retrieves node information through authenticated TCP communication and displays it in a browser.

The application is available locally through Streamlit.

## Testing and Results

### Test 1 – Persistent Journal Storage

Tested the JSONL journal by recording task information and loading the journal again.

Verified that previously recorded task information could be reconstructed.

**Result: Persistent journal storage verified.**

### Test 2 – Task Recovery After Restart

Tested recovery of an unfinished task.

Observed the following behavior:

- Task was initially marked RUNNING.
- Task information was stored in the journal.
- The task store was initialized again.
- The unfinished task was recovered.
- Its status changed back to PENDING.
- The task was added to the pending queue.

Example test output:

`Before restart: RUNNING`

`After restart: PENDING`

`Recovered task: T201`

**Result: Unfinished task recovery verified.**

### Test 3 – HMAC-SHA256 Authentication

Tested message signing and verification.

Verified that:

- A correctly signed message passed verification.
- A modified message failed verification.

Example test output:

`Valid: True`

`Tampered: False`

**Result: Message authentication and tamper detection verified.**

### Test 4 – Authenticated Multi-Node Communication

Started multiple MeshWeaver nodes using separate terminals with the same configured shared secret.

Verified authenticated communication for TCP requests, responses and resource reports.

Observed successful resource information exchange between active peers.

**Result: Authenticated node communication verified.**

### Test 5 – Indirect Peer Discovery

Tested peer-list gossip using three nodes:

- NODE_A – TCP port 8001
- NODE_B – TCP port 8002
- NODE_C – TCP port 8003

Configured NODE_B and NODE_C to announce only to NODE_A.

Verified that NODE_A shared its known peer information with the other nodes.

Observed the following log messages:

`Learned peer NODE_C indirectly through NODE_A`

`Learned peer NODE_B indirectly through NODE_A`

This demonstrated that NODE_B and NODE_C could learn about each other through NODE_A without directly receiving each other's announcements.

**Result: Controlled indirect peer discovery verified in both directions.**

### Test 6 – Terminal Dashboard

Started the three-node cluster and launched the terminal monitoring dashboard.

Verified:

- All three nodes appeared online.
- CPU and RAM information was displayed.
- Peer states were visible.
- Task queue information was retrieved.

**Result: Terminal monitoring dashboard verified.**

### Test 7 – Web Dashboard

Launched the Streamlit dashboard in a separate terminal.

Verified that the browser dashboard displayed:

- Total nodes: 3
- Online nodes: 3
- Offline nodes: 0
- CPU and RAM utilization.
- Peer counts.
- Task queue statistics.
- Individual node information.

**Result: Web-based cluster monitoring verified.**

## How to Run

Run the following commands from the `day5_wk1` directory.

### 1. Configure the Shared Secret

Set the environment variable in every terminal used to start a node:

```powershell
$env:MESHWEAVER_SECRET = "MeshWeaver-Dev-Secret-ChangeThis-2026"
```

All nodes participating in the same cluster must use the same secret.

### 2. Start Node 1

Open the first terminal:

```powershell
python node.py --tcp 8001 --id NODE_A
```

### 3. Start Node 2

Open a second terminal:

```powershell
python node.py --tcp 8002 --id NODE_B
```

### 4. Start Node 3

Open a third terminal:

```powershell
python node.py --tcp 8003 --id NODE_C
```

Keep all three nodes running to allow peer discovery, resource gossip and task execution.

### 5. Run the Terminal Dashboard

Open another terminal:

```powershell
$env:MESHWEAVER_SECRET = "MeshWeaver-Dev-Secret-ChangeThis-2026"
python dashboard.py
```

### 6. Run the Web Dashboard

Open another terminal:

```powershell
$env:MESHWEAVER_SECRET = "MeshWeaver-Dev-Secret-ChangeThis-2026"
python -m streamlit run web_dashboard.py
```

Open the local Streamlit address displayed in the terminal, normally:

`http://localhost:8501`

## Known Limitations

- The journal provides recovery of recorded task state, but does not guarantee exactly-once task execution.
- A task interrupted during execution may be executed again after recovery.
- HMAC authentication depends on securely configuring and sharing the same secret across participating nodes.
- Timestamp freshness checks are implemented, but a dedicated nonce-based replay prevention mechanism is not yet implemented.
- Indirectly discovered peers remain UNKNOWN until directly discovered.
- Peer discovery still uses configured UDP seed ports; a Kademlia-based DHT is not yet implemented.
- The web dashboard currently uses manual refresh rather than continuous automatic browser refresh.
- The current implementation has been tested with a three-node local cluster; larger-scale distributed testing remains pending.
- Advanced failure recovery, task reassignment and network partition handling require further testing and integration.

## Technologies Used

- Python
- Asyncio
- TCP and UDP sockets
- JSON
- JSON Lines (JSONL)
- HMAC-SHA256
- Hashlib
- HMAC
- Environment Variables
- Streamlit
- psutil
- Logging
- UUID
- Dataclasses
- Time and persistent storage

## Conclusion

Day 5 enhances MeshWeaver with persistent task recovery, authenticated communication, indirect peer discovery and cluster monitoring.

These additions improve the reliability, security and observability of the decentralized task broker while extending its peer-to-peer networking capabilities.