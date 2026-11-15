# MeshWeaver

## Project Overview

MeshWeaver is a Python-based peer-to-peer asynchronous task broker designed to allow multiple nodes to communicate, exchange information, monitor resources, and distribute tasks efficiently.

The project explores asynchronous networking, peer discovery, node health monitoring, resource sharing, load-aware scheduling, distributed task execution, persistent task recovery, message authentication, and system monitoring.

## Project Objectives

- Establish communication between peer nodes.
- Discover and monitor the health of network nodes.
- Exchange system resource information.
- Distribute tasks between available nodes.
- Support reliable task execution and result transfer.
- Handle task failures, retries, and communication issues.
- Improve resource utilization through load-aware scheduling.
- Recover unfinished tasks after node restarts.
- Secure node communication through message authentication.
- Monitor the status and performance of the distributed network.

## Technology Stack

- Python
- Asyncio
- UDP and TCP networking
- JSON message framing
- Psutil for system resource monitoring
- HMAC-SHA256 for message authentication
- Streamlit for web-based monitoring
- Git and GitHub

## Week 1 Progress

| Day | Work | Status |
|---|---|---|
| Day 1 | UDP communication, RTT measurement, jitter, packet loss and network-health classification | Completed |
| Day 2 | TCP communication, message framing, server monitoring and multiple-client testing | Completed |
| Day 3 | Peer discovery, failure detection, asynchronous task queue and task recovery testing | Completed |
| Day 4 | Resource monitoring, resource gossip, load-aware scheduling, task forwarding, remote execution and automatic retries | Completed |
| Day 5 | Persistent task journaling, HMAC authentication, indirect peer discovery and monitoring dashboards | Completed |
| Day 6 | Further integration, result handling and distributed execution testing | Planned |
| 16 November | Additional testing, documentation and reliability improvements | Planned |

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
├── day5_wk1/
│   ├── discovery.py
│   ├── peer_table.py
│   ├── framing.py
│   ├── node.py
│   ├── resource_monitor.py
│   ├── resource_gossip.py
│   ├── scheduler.py
│   ├── worker.py
│   ├── task_store.py
│   ├── journal.py
│   ├── security.py
│   ├── cluster_test.py
│   ├── test_journal.py
│   ├── test_task_recovery.py
│   ├── dashboard.py
│   ├── web_dashboard.py
│   └── README.md
│
├── .gitignore
├── README.md
└── requirements.txt
```

## Current Progress

### Day 1 – UDP Communication

Implemented asynchronous UDP sender and listener communication using PING/PONG messages.

Added RTT measurement, jitter calculation, packet-loss measurement, and basic network-health classification to evaluate communication performance.

### Day 2 – TCP Communication

Implemented TCP client-server communication with length-prefixed JSON message framing.

Added HELLO, ADD, TIME and STATUS requests, server uptime and request monitoring, active-client tracking, and concurrent client testing.

### Day 3 – Peer Discovery and Task Management

Implemented UDP-based peer discovery using periodic ANNOUNCE messages.

Added peer health monitoring with ALIVE, SUSPECT and DEAD states, along with failure detection and recovery event logging.

Developed an asynchronous FIFO task queue supporting task submission, retrieval, completion, status tracking, and recovery of unfinished tasks.

Tested multi-node discovery, peer failure detection, recovery events, and task queue operations. The cluster integration test passed all 11 checks.

### Day 4 – Resource Monitoring and Distributed Task Execution

Implemented system resource monitoring using CPU utilization, RAM utilization, and active task count.

Developed resource gossip to exchange load reports between active peer nodes periodically.

Introduced a load-aware scheduler that selects the least-loaded available peer using resource reports and node health information.

Extended task management with task forwarding, remote execution, and result retrieval between nodes.

Implemented a worker system supporting task operations such as ADD, SUBTRACT, MULTIPLY, DIVIDE, and ECHO.

Added automatic task retries with a maximum retry limit and exponential backoff to improve task execution reliability.

Tested a two-node local cluster, resource report exchange, remote task forwarding, successful task execution, and failure handling.

### Day 5 – Persistence, Security, Peer Gossip and Monitoring

Implemented an append-only JSON Lines task journal to record task state changes persistently.

Added task recovery after restart by replaying journal entries and restoring unfinished tasks. Tasks that were in the RUNNING state during shutdown are returned to PENDING for possible re-execution.

Integrated HMAC-SHA256 message authentication to sign and verify communication messages. Authentication is applied to TCP requests and responses, UDP discovery beacons, and resource gossip reports.

Enhanced peer discovery with indirect peer learning through exchanged peer information. Nodes can learn about peers through another known node without requiring direct initial contact.

Maintained a distinction between directly connected peers and indirectly learned peers so that indirect peers are not treated as confirmed active nodes.

Developed a terminal-based monitoring dashboard displaying node status, CPU usage, RAM usage, active tasks, queue information, and peer health.

Added a Streamlit-based web dashboard to monitor multiple nodes through a browser, including node availability, resource utilization, peer information, and task queue statistics.

Tested task journaling, restart recovery, message authentication, tamper detection, indirect peer discovery, authenticated communication, and dashboard monitoring in a local multi-node environment.

## Upcoming Development

The next development stages focus on:

1. Further integration of distributed task execution and result handling.
2. Advanced task serialization and deserialization using cloudpickle.
3. Improving task recovery when a remote node becomes unavailable.
4. Enhancing worker concurrency and retry handling.
5. Strengthening replay protection and communication security.
6. Exploring more scalable peer discovery approaches, including DHT-based discovery.
7. Performing larger multi-node testing and documenting performance.

## Documentation

- [Day 1 – UDP Communication](day1_wk1/README.md)
- [Day 2 – TCP Communication](day2_wk1/README.md)
- [Day 3 – Peer Discovery and Task Management](day3_wk1/README.md)
- [Day 4 – Resource Monitoring and Distributed Task Execution](day4_wk1/README.md)
- [Day 5 – Persistence, Security, Peer Gossip and Monitoring](day5_wk1/README.md)

## Current Limitations

- Peer discovery currently uses UDP beacons and configured seed ports; a full Kademlia DHT is not yet implemented.
- Indirectly learned peers remain unconfirmed until direct communication establishes their availability.
- HMAC authentication currently relies on a shared secret configured through an environment variable.
- Timestamp-based message freshness checks are implemented, but a dedicated nonce-based replay-prevention mechanism is not yet available.
- Task recovery does not guarantee exactly-once execution. A task may be executed again after recovery if its previous execution completed but its final state was not recorded.
- Persistent journaling records task state changes, but does not provide a fully persistent distributed result store.
- The web dashboard currently uses manual refresh rather than continuous automatic refresh.
- Testing has primarily been performed in controlled local multi-node environments; larger network and failure scenarios require further validation.

## Conclusion

MeshWeaver has progressed from basic UDP and TCP communication to a multi-node asynchronous task broker with peer discovery, resource monitoring, load-aware scheduling, distributed task execution, retry handling, persistent task recovery, authenticated communication, and monitoring dashboards.

The completed work establishes a foundation for a more reliable and scalable decentralized task-processing system. Further development will focus on integration, advanced task serialization, security improvements, and extensive distributed testing.
