# MeshWeaver

## Project Overview

MeshWeaver is a Python-based peer-to-peer asynchronous task broker designed to allow multiple nodes to communicate, exchange information, monitor resources, and distribute computational tasks efficiently.

The project explores asynchronous networking, peer discovery, node health monitoring, resource sharing, load-aware scheduling, distributed task execution, function serialization, persistent task recovery, message authentication, system monitoring, and journal integrity auditing.

Unlike traditional centralized task brokers, MeshWeaver aims to distribute task-processing responsibilities across multiple connected nodes without depending on a central message broker such as Redis or RabbitMQ.

## Project Objectives

- Establish communication between peer nodes.
- Discover and monitor the health of network nodes.
- Exchange system resource information.
- Distribute tasks between available nodes.
- Support remote function execution and result retrieval.
- Handle task failures, retries, and communication issues.
- Improve resource utilization through load-aware scheduling.
- Recover unfinished tasks after node restarts.
- Secure node communication through message authentication.
- Serialize and transfer Python functions between nodes.
- Monitor the status and performance of the distributed network.
- Verify persistent task recovery and detect journal inconsistencies.
- Explore scalable decentralized peer discovery mechanisms.

## Technology Stack

- Python
- Asyncio
- UDP and TCP networking
- JSON message framing
- Psutil for system resource monitoring
- HMAC-SHA256 for message authentication
- Cloudpickle for Python function serialization
- Base64 for encoded serialized data
- Streamlit for web-based monitoring
- Pytest and Python test scripts for automated testing
- Git and GitHub

## Week 1 Progress

| Day | Work | Status |
|---|---|---|
| Day 1 | UDP communication, PING/PONG, RTT measurement, jitter and packet-loss monitoring | Completed |
| Day 2 | TCP communication, length-prefixed message framing and concurrent client testing | Completed |
| Day 3 | Peer discovery, failure detection, asynchronous task queue and task recovery testing | Completed |
| Day 4 | Resource monitoring, resource gossip, load-aware scheduling, task forwarding and remote execution | Completed |
| Day 5 | Persistent task journaling, HMAC authentication, indirect peer discovery and monitoring dashboards | Completed |
| Day 6 | Persistent recovery verification, journal integrity auditing and automated testing | Completed |
| Day 7 | Function serialization, remote function execution and two-node load-based task distribution | Completed |

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
├── day6_wk1/
│   ├── recovery_audit.py
│   ├── test_recovery.py
│   ├── test_journal_integrity.py
│   ├── test_recovery_report.py
│   ├── test_node_recovery.py
│   └── README.md
│
├── day7_wk1/
│   ├── serializer.py
│   ├── test_serialization.py
│   ├── test_worker.py
│   ├── test_remote_execution.py
│   ├── test_load_balance.py
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

Introduced a load-aware scheduler that selects a less-loaded available peer using resource reports and node health information.

Extended task management with task forwarding, remote execution, and result retrieval between nodes.

Implemented a worker system supporting task operations such as ADD, SUBTRACT, MULTIPLY, DIVIDE, and ECHO.

Added automatic task retries with a maximum retry limit and exponential backoff to improve task execution reliability.

Tested a two-node local cluster, resource report exchange, remote task forwarding, successful task execution, and failure handling.

### Day 5 – Persistence, Security, Peer Gossip and Monitoring

Implemented an append-only JSON Lines task journal to record task state changes persistently.

Added task recovery after restart by replaying journal entries and restoring unfinished tasks. Tasks that were in the RUNNING state during shutdown are returned to PENDING for possible re-execution.

Integrated HMAC-SHA256 message authentication to sign and verify communication messages. Authentication is applied to TCP requests and responses, UDP discovery messages, and resource gossip reports.

Enhanced peer discovery with indirect peer learning through exchanged peer information. Nodes can learn about peers through another known node without requiring direct initial contact.

Maintained a distinction between directly connected peers and indirectly learned peers so that indirect peers are not treated as confirmed active nodes.

Developed a terminal-based monitoring dashboard displaying node status, CPU usage, RAM usage, active tasks, queue information, and peer health.

Added a Streamlit-based web dashboard to monitor multiple nodes through a browser, including node availability, resource utilization, peer information, and task queue statistics.

Tested task journaling, restart recovery, message authentication, tamper detection, indirect peer discovery, authenticated communication, and dashboard monitoring in a local multi-node environment.

### Day 6 – Persistent Recovery Verification and Journal Integrity Auditing

Extended the persistence and recovery work from Day 5 by verifying that task states are correctly restored after restarting the task store and node.

Implemented automated recovery tests to check the restoration of RUNNING tasks as PENDING, preservation of completed tasks, and recovery of multiple tasks from the same journal.

Updated the Node constructor to support a configurable journal path, allowing recovery tests to use temporary journal files without interfering with existing node data.

Developed a recovery auditing utility to inspect JSON Lines task journals and generate reports containing total tasks, task statuses, total journal events, and interrupted tasks.

Added journal integrity checks to identify malformed entries, orphan updates, and duplicate task records.

Implemented interrupted-task detection to identify tasks that were recorded as RUNNING and may require re-execution after a restart.

Added a recovery report displaying task counts, status distribution, interrupted tasks, and journal health warnings.

Verified that incomplete or malformed journal entries are skipped during journal replay while valid task records are restored.

Tested the recovery auditor using actual journal files and a demonstration journal containing an interrupted task and a malformed entry.

Executed the automated Day 6 test suite successfully, with all 9 tests passing and no failures.

### Day 7 – Function Serialization, Remote Execution and Load-Based Task Distribution

Implemented Python function serialization and deserialization using Cloudpickle.

Developed a serializer module that converts Python functions, positional arguments, and keyword arguments into Base64-encoded serialized packages for transfer between nodes.

Added input validation, Base64 decoding validation, and a maximum serialized payload size of 700 KB.

Integrated a new REMOTE_CALL operation into the existing worker system, allowing a receiving node to reconstruct and execute serialized Python functions.

Connected remote function execution with the existing task queue and task result management system.

Enhanced task distribution to compare local and peer load scores and forward tasks to a less-loaded available peer.

Integrated authenticated TCP communication into remote task forwarding and response handling using the existing HMAC-SHA256 security mechanism.

Added remote task tracking to maintain information about the peer responsible for executing forwarded tasks.

Created dedicated tests for function serialization, worker execution, remote function execution, and load-based task forwarding.

Verified successful serialization and execution of a multiplication function:

`multiply(10, 20) = 200`

Tested remote execution through a MeshWeaver node and verified successful task result retrieval.

Performed a two-node distributed execution test using Node 1 on TCP port 8001 and Node 2 on TCP port 8002.

Submitted eight tasks through Node 1. All eight tasks were successfully forwarded to Node 2, accepted by its worker, executed, and marked as completed.

This demonstrated successful load-based task distribution and remote execution across two independent MeshWeaver nodes.

## Week 1 Overall Achievements

By the end of Week 1, MeshWeaver progressed from basic network communication to a distributed task-processing system with the following capabilities:

- Asynchronous UDP and TCP communication.
- Peer discovery and peer health monitoring.
- Asynchronous task queue management.
- CPU and RAM monitoring.
- Periodic resource gossip.
- Load-aware task scheduling.
- Task forwarding between connected nodes.
- Remote task execution.
- Automatic task retry handling.
- Persistent task journaling and recovery.
- HMAC-SHA256 message authentication.
- Direct and indirect peer discovery.
- Terminal and web-based monitoring dashboards.
- Journal integrity auditing.
- Python function serialization and deserialization.
- Distributed execution of serialized functions.

## Upcoming Development – Week 2

The next development phase will focus on improving decentralized peer discovery, routing, and distributed execution.

Planned development areas include:

1. Understanding and implementing XOR-based node distance calculation.
2. Building a Distributed Hash Table (DHT) foundation.
3. Implementing node lookup and peer routing mechanisms.
4. Exploring Kademlia-style peer discovery.
5. Improving distributed task routing across multiple nodes.
6. Handling unavailable peers and routing failures.
7. Testing peer discovery and routing in larger multi-node environments.
8. Improving integration between task distribution, execution and result retrieval.

These are planned enhancements and have not yet been implemented.

## Documentation

- [Day 1 – UDP Communication](day1_wk1/README.md)
- [Day 2 – TCP Communication](day2_wk1/README.md)
- [Day 3 – Peer Discovery and Task Management](day3_wk1/README.md)
- [Day 4 – Resource Monitoring and Distributed Task Execution](day4_wk1/README.md)
- [Day 5 – Persistence, Security, Peer Gossip and Monitoring](day5_wk1/README.md)
- [Day 6 – Persistent Recovery Verification and Journal Integrity Auditing](day6_wk1/README.md)
- [Day 7 – Function Serialization, Remote Execution and Load-Based Task Distribution](day7_wk1/README.md)

## Current Limitations

- Peer discovery currently uses UDP announcements and configured seed ports; a full Kademlia-based DHT is not yet implemented.
- Indirectly learned peers remain unconfirmed until direct communication establishes their availability.
- HMAC authentication relies on a shared secret configured through an environment variable.
- Timestamp-based message freshness checks are implemented, but a dedicated nonce-based replay-prevention mechanism is not yet available.
- Task recovery does not guarantee exactly-once execution. A task may be executed again after recovery if its previous execution completed but its final state was not recorded.
- Persistent journaling records task state changes, but does not provide a fully persistent distributed result store.
- The recovery auditor detects journal inconsistencies but does not automatically repair or truncate damaged journal files.
- Incomplete or malformed journal entries are skipped during replay; automatic journal repair is not implemented.
- Cloudpickle deserialization can execute arbitrary code. Remote function packages must only be accepted from trusted and authenticated peers; authentication alone does not provide a sandbox.
- Load-aware scheduling depends on the availability and freshness of peer resource reports.
- The current distributed execution test demonstrates forwarding and successful execution across two local nodes. Larger-scale cluster testing remains pending.
- Advanced failure recovery, automatic remote task reassignment, and network partition handling require further development.
- The web dashboard currently uses manual refresh rather than continuous automatic refresh.
- Testing has primarily been performed in controlled local multi-node environments; larger network and failure scenarios require further validation.

## Conclusion

MeshWeaver has progressed from basic UDP and TCP communication to a multi-node asynchronous task broker with peer discovery, resource monitoring, load-aware scheduling, distributed task execution, retry handling, persistent task recovery, authenticated communication, monitoring dashboards, journal integrity auditing, and Python function serialization.

The successful execution of eight forwarded tasks across two independent nodes demonstrates the progress made toward decentralized computational task distribution.

Week 1 establishes the foundation for distributed task processing. The next phase will focus on scalable peer discovery, DHT-based routing, and improved coordination between distributed nodes.

The long-term goal is to develop a reliable, secure, and scalable peer-to-peer asynchronous task broker without depending on a centralized message broker.