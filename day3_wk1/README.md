# Day 3 – Peer Discovery, Failure Detection and Task Queue

## Overview

Day 3 focuses on peer discovery, node health monitoring and asynchronous task management in MeshWeaver. It introduces UDP-based peer discovery, peer state tracking, failure detection, task queue management and recovery of unfinished tasks.

## Project Files

| File | Purpose |
|---|---|
| `peer_table.py` | Stores peers and manages their states |
| `discovery.py` | Handles UDP ANNOUNCE beacons for peer discovery |
| `task_queue.py` | Implements an asynchronous FIFO task queue |
| `node.py` | Runs peer discovery, failure detection and the TCP server |
| `framing.py` | Handles length-prefixed JSON message framing (from Day 2) |
| `cluster_test.py` | Tests peer discovery and task queue operations |
| `test_peer_table.py` | Tests peer state transitions |
| `test_task_recovery.py` | Tests recovery and reassignment of unfinished tasks |

## Features Implemented

### 1. Peer Discovery

Uses UDP ANNOUNCE beacons to allow nodes to discover configured peers.

- Nodes periodically broadcast their presence every 2 seconds.
- Newly discovered peers are registered in the peer table.
- Nodes ignore their own announcements.
- Invalid discovery packets are ignored and logged.

### 2. Peer Health Monitoring

Tracks peer availability using timestamps and three states:

| State | Condition |
|---|---|
| ALIVE | Beacon received within 6 seconds |
| SUSPECT | No beacon for more than 6 seconds |
| DEAD | No beacon for more than 15 seconds |

A background reaper loop periodically checks peer states and detects failures.

When a previously unavailable node sends a new announcement, its state returns to ALIVE and a recovery event is logged.

### 3. Asynchronous Task Queue

Implemented an asynchronous FIFO task queue with the following operations:

- Task submission
- Task retrieval
- Task completion
- Task status tracking
- Requeueing unfinished tasks assigned to failed workers

The task lifecycle follows:

`PENDING → RUNNING → DONE`

If a worker is declared DEAD, its unfinished RUNNING tasks are returned to the PENDING queue for reassignment.

### 4. TCP Request Handling

Extended the Day 2 TCP server to support peer and task management requests.

| Request | Server Response | Purpose |
|---|---|---|
| `PEERS` | `PEERS_RESPONSE` | Returns the peer table |
| `SUBMIT_TASK` | `TASK_ACCEPTED` | Adds a task to the queue |
| `GET_TASK` | `TASK` / `NO_TASK` | Retrieves the oldest pending task |
| `COMPLETE_TASK` | `TASK_DONE` / `ERROR` | Marks a running task as completed |
| `QUEUE_STATUS` | `QUEUE_STATUS_RESPONSE` | Returns pending, running and done counts |
| Unknown request | `ERROR` | Reports an unsupported request |

## Testing and Results

### Test 1 – Multi-Node Peer Discovery

Started three nodes using separate terminals.

All three nodes successfully discovered one another and registered their peers.

### Test 2 – Peer Failure Detection and Recovery

Stopped a running node and observed the following transitions:

`ALIVE → SUSPECT → DEAD`

Restarted the node using the same node ID and verified that the recovery event was logged.

### Test 3 – Cluster Integration Testing

Implemented `cluster_test.py` to verify peer discovery and task queue operations.

Successfully passed all 11 checks:

- Peer discovery and ALIVE status verification.
- Task submission and pending queue count.
- FIFO task retrieval in A, B, C order.
- Empty queue handling.
- Successful task completion.
- Duplicate completion rejection.
- Queue statistics verification.
- Unknown request and unknown task ID handling.

**Result: 11/11 checks passed.**

### Test 4 – Task Recovery

Implemented `test_task_recovery.py` to simulate worker failure.

- Submitted a task and assigned it to Node-1.
- Simulated worker failure.
- Requeued the unfinished task.
- Successfully reassigned the same task to Node-2.

**Result: Task recovery test passed.**

*Note: This test verifies recovery within a single TaskQueue instance, not task transfer between separate node processes.*

## How to Run

Run these commands from the project root directory.

**Start three nodes in separate terminals:**

Terminal 1:
```bash
python day3_wk1/node.py
```
Enter Node ID `Node 1` and TCP port `5001`.

Terminal 2:
```bash
python day3_wk1/node.py
```
Enter Node ID `Node 2` and TCP port `5002`.

Terminal 3:
```bash
python day3_wk1/node.py
```
Enter Node ID `Node 3` and TCP port `5003`.

**Run the cluster integration test:**

```bash
python day3_wk1/cluster_test.py
```

**Run the task recovery test:**

```bash
python day3_wk1/test_task_recovery.py
```

**Run the peer table test:**

```bash
python day3_wk1/test_peer_table.py
```

Keep the nodes running in separate terminals while executing the cluster integration test.

## Known Limitations

- Task queues are maintained independently by each node and stored in memory.
- Discovery currently uses localhost and a fixed seed port list (50001–50003).
- Cross-node task migration and recovery are not yet implemented.
- Task requeue depends on matching the worker ID with the failed node ID.
- Duplicate task submission protection is not yet implemented.

## Technologies Used

- Python
- Asyncio
- UDP and TCP sockets
- JSON
- UUID
- Dataclasses
- Logging