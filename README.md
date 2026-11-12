# MeshWeaver

## Project Overview

MeshWeaver is a Python-based peer-to-peer asynchronous task broker designed to allow multiple nodes to communicate, exchange information, and manage tasks efficiently.

The project explores asynchronous networking, peer discovery, node health monitoring, task management, serialization, and distributed task execution.

## Project Objectives

- Establish communication between peer nodes.
- Discover and monitor the health of network nodes.
- Exchange system resource information.
- Distribute tasks between available nodes.
- Support reliable task execution and result transfer.
- Handle node failures and communication issues.

## Technology Stack

- Python
- Asyncio
- UDP and TCP networking
- JSON message framing
- Python serialization
- Git and GitHub

## Week 1 Progress

| Day | Work | Status |
|---|---|---|
| Day 1 | UDP communication, RTT, jitter, packet loss and network-health classification | Completed |
| Day 2 | TCP communication, message framing, server monitoring and multiple-client testing | Completed |
| Day 3 | Peer discovery, failure detection, asynchronous task queue and task recovery testing | Completed |
| Day 4 | Task serialization and deserialization | Planned |
| Day 5 | Task transfer between nodes | Planned |
| Day 6 | Task execution, result transfer and integration | Planned |
| 16 November | Testing, documentation, HMAC authentication and reliability improvements | Planned |

## Project Structure

```text
MeshWeaver/
│
├── day1_wk1/
│   ├── sender.py
│   ├── listener.py
│   └── README.md
│
├── day2_wk1/
│   ├── framing.py
│   ├── tcp_client.py
│   ├── tcp_server.py
│   ├── multi_client_test.py
│   └── README.md
│
├── day3_wk1/
│   ├── discovery.py
│   ├── peer_table.py
│   ├── task_queue.py
│   ├── framing.py
│   ├── node.py
│   ├── cluster_test.py
│   ├── test_peer_table.py
│   ├── test_task_recovery.py
│   └── README.md
│
├── .gitignore
├── README.md
└── requirements.txt
```

## Current Progress

### Day 1 – UDP Communication

Implemented asynchronous UDP sender and listener communication using PING/PONG messages. Added RTT, jitter, packet-loss measurement and basic network-health classification.

### Day 2 – TCP Communication

Implemented TCP client-server communication with length-prefixed JSON framing. Added HELLO, ADD, TIME and STATUS requests, server uptime and request monitoring, active-client tracking, and concurrent client testing.

### Day 3 – Peer Discovery and Task Management

Implemented UDP-based peer discovery using periodic ANNOUNCE messages. Added peer health monitoring with ALIVE, SUSPECT and DEAD states, along with failure detection and recovery event logging.

Developed an asynchronous FIFO task queue supporting task submission, retrieval, completion, status tracking and simulated recovery of unfinished tasks.

Tested multi-node discovery, peer failure detection, recovery events and task queue operations. The cluster integration test passed all 11 checks.

## Upcoming Development

The next development stages focus on:

1. Task serialization and deserialization.
2. Transferring serialized tasks between nodes through TCP.
3. Executing received tasks and returning results.
4. Integrating task distribution with peer discovery and node monitoring.
5. Implementing authentication, failure handling and reliability improvements.

## Documentation

- [Day 1 – UDP Communication](day1_wk1/README.md)
- [Day 2 – TCP Communication](day2_wk1/README.md)
- [Day 3 – Peer Discovery and Task Management](day3_wk1/README.md)

## Current Limitations

- Peer discovery currently uses localhost and configured seed ports.
- Task queues are maintained independently by each node.
- Cross-node task transfer and distributed execution are not yet implemented.
- Task recovery has been tested within a single queue instance.

## Project Status

Week 1 development is in progress. Day 1, Day 2 and Day 3 tasks have been completed. Distributed task transfer, execution and other planned features are still under development.
