# MeshWeaver

## Project Overview

MeshWeaver is a Python-based peer-to-peer asynchronous task broker designed to allow multiple nodes to communicate, exchange information, monitor resources, and distribute tasks efficiently.

The project explores asynchronous networking, peer discovery, node health monitoring, resource sharing, task management, load-aware scheduling, and distributed task execution.

## Project Objectives

- Establish communication between peer nodes.
- Discover and monitor the health of network nodes.
- Exchange system resource information.
- Distribute tasks between available nodes.
- Support reliable task execution and result transfer.
- Handle task failures, retries, and communication issues.
- Improve resource utilization through load-aware scheduling.

## Technology Stack

- Python
- Asyncio
- UDP and TCP networking
- JSON message framing
- Psutil for system resource monitoring
- Git and GitHub

## Week 1 Progress

| Day | Work | Status |
|---|---|---|
| Day 1 | UDP communication, RTT measurement, jitter, packet loss and network-health classification | Completed |
| Day 2 | TCP communication, message framing, server monitoring and multiple-client testing | Completed |
| Day 3 | Peer discovery, failure detection, asynchronous task queue and task recovery testing | Completed |
| Day 4 | Resource monitoring, resource gossip, load-aware scheduling, task forwarding, remote execution and automatic retries | Completed |
| Day 5 | Advanced task serialization and reliability improvements | Planned |
| Day 6 | Further integration, result handling and distributed execution testing | Planned |
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
├── day4_wk1/
│   ├── node.py
│   ├── resource_monitor.py
│   ├── resource_gossip.py
│   ├── scheduler.py
│   ├── task_store.py
│   ├── worker.py
│   └── README.md
│
├── .gitignore
├── README.md
└── requirements.txt
```

## Current Progress

### Day 1 – UDP Communication

Implemented asynchronous UDP sender and listener communication using PING/PONG messages.

Added RTT measurement, jitter calculation, packet-loss measurement and basic network-health classification.

### Day 2 – TCP Communication

Implemented TCP client-server communication with length-prefixed JSON framing.

Added HELLO, ADD, TIME and STATUS requests, server uptime and request monitoring, active-client tracking, and concurrent client testing.

### Day 3 – Peer Discovery and Task Management

Implemented UDP-based peer discovery using periodic ANNOUNCE messages.

Added peer health monitoring with ALIVE, SUSPECT and DEAD states, along with failure detection and recovery event logging.

Developed an asynchronous FIFO task queue supporting task submission, retrieval, completion, status tracking and recovery of unfinished tasks.

Tested multi-node discovery, peer failure detection, recovery events and task queue operations. The cluster integration test passed all 11 checks.

### Day 4 – Resource Monitoring and Distributed Task Execution

Implemented system resource monitoring using CPU utilization, RAM utilization and active task count.

Developed resource gossip to exchange load reports between active peer nodes periodically.

Introduced a load-aware scheduler that selects the least-loaded available peer using resource reports and node health information.

Extended task management with task forwarding, remote execution and result retrieval between nodes.

Implemented a worker system supporting task operations such as ADD, SUBTRACT, MULTIPLY, DIVIDE and ECHO.

Added automatic task retries with a maximum retry limit and exponential backoff to improve task execution reliability.

Tested a two-node local cluster, resource report exchange, remote task forwarding, successful task execution and failure handling.

## Upcoming Development

The next development stages focus on:

1. Advanced task serialization and deserialization using cloudpickle.
2. Improving distributed task transfer and execution reliability.
3. Enhancing task recovery when a remote node becomes unavailable.
4. Improving worker concurrency and retry handling.
5. Integrating stronger authentication using HMAC.
6. Performing larger multi-node testing and documentation.

## Documentation

- [Day 1 – UDP Communication](day1_wk1/README.md)
- [Day 2 – TCP Communication](day2_wk1/README.md)
- [Day 3 – Peer Discovery and Task Management](day3_wk1/README.md)
- [Day 4 – Resource Monitoring and Distributed Task Execution](day4_wk1/README.md)

## Current Limitations

- Peer discovery currently uses UDP beacons and configured seed ports; a full Kademlia DHT is not yet implemented.
- Resource reports can become stale if a peer stops responding.
- Task and result information is maintained in memory and is not persistent.
- The current worker performs