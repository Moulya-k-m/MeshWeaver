
# MeshWeaver

## Project Overview

MeshWeaver is a Python-based peer-to-peer asynchronous task broker that enables multiple nodes to communicate, discover peers, exchange resources, and distribute computational tasks without relying on centralized brokers such as Redis or RabbitMQ.

## Objectives

- Establish asynchronous communication between peer nodes.
- Discover peers and monitor node health.
- Exchange CPU and RAM utilization information.
- Distribute tasks using load-aware scheduling.
- Support remote function execution and result retrieval.
- Handle failures, retries, and task recovery.
- Secure communication using message authentication.
- Implement decentralized peer discovery using Kademlia-inspired mechanisms.

## Technology Stack

Python, Asyncio, UDP, TCP, JSON, Psutil, HMAC-SHA256, Cloudpickle, Base64, Secrets, Dataclasses, Streamlit, Unittest, Git and GitHub.

## Week 1 Progress

| Day | Work | Status |
|---|---|---|
| Day 1 | UDP communication, PING/PONG, RTT, jitter and packet-loss monitoring | Completed |
| Day 2 | TCP communication, JSON framing and concurrent client testing | Completed |
| Day 3 | Peer discovery, failure detection, asynchronous task queue and recovery | Completed |
| Day 4 | Resource monitoring, gossip, load-aware scheduling and remote execution | Completed |
| Day 5 | Persistent journaling, HMAC security, peer gossip and monitoring dashboards | Completed |
| Day 6 | Task recovery verification and journal integrity auditing | Completed |
| Day 7 | Function serialization, remote execution and load-based task distribution | Completed |

## Week 2 Progress

| Day | Work | Status |
|---|---|---|
| Day 8 | DHT foundation, 160-bit node identities, XOR distance and peer information | Completed |
| Day 9 | Kademlia-inspired routing table, K-Buckets and closest-peer lookup | Completed |
| Day 10 | Bootstrap mechanism, dynamic node joining and peer discovery | Completed |
| Day 11 | FIND_NODE protocol and iterative peer lookup | Completed |
| Day 12 | Resource monitoring and CPU/RAM status collection | Planned |
| Day 13 | Asynchronous background gossip with 5-second updates | Planned |
| Day 14 | DHT and gossip integration, multi-node testing and reliability improvements | Planned |


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
├── day8_wk2/
│   ├── node_identity.py
│   ├── peer_info.py
│   ├── test_day8.py
│   ├── test_edge_cases.py
│   ├── test_serialization.py
│   └── README.md
│
├── day9_wk2/
│   ├── __init__.py
│   ├── peer.py
│   ├── routing_table.py
│   ├── test_routing.py
│   └── README.md
│
├── day10_wk2/
│   ├── __init__.py
│   ├── bootstrap.py
│   ├── peer_discovery.py
│   ├── test_discovery.py
│   └── README.md
│
├── day11_wk2/
│   ├── __init__.py
│   ├── find_node.py
│   ├── test_find_node.py
│   ├── lookup_manager.py
│   ├── test_lookup_manager.py
│   └── README.md
│
├── .gitignore
├── README.md
└── requirements.txt
```




Each day folder contains its implementation, tests and README documentation.

## Current Progress

### Week 1 – Distributed Task Processing

Implemented asynchronous UDP and TCP communication, peer discovery, health monitoring, task queue management, resource monitoring, gossip, load-aware scheduling and remote task execution.

Added persistent task journaling, restart recovery, HMAC-SHA256 authentication, indirect peer discovery, terminal and web dashboards, and journal integrity auditing.

Implemented Python function serialization using Cloudpickle and Base64, enabling remote function execution between nodes.

Verified distributed execution using two local nodes, successfully forwarding and completing eight tasks.

### Week 2 – Decentralized Peer Discovery

**Day 8 – DHT Foundation**

Implemented 160-bit node identity generation and validation, XOR distance calculation, and peer information management using dataclasses and JSON serialization.

**Day 9 – Kademlia Routing Table**

Implemented 160 K-Buckets, peer insertion and removal, duplicate detection, full-bucket replacement support, closest-peer lookup and routing table statistics.

**Day 10 – Bootstrap and Dynamic Node Joining**

Developed a TCP-based bootstrap server and JOIN request-response mechanism. New nodes can register with the network, discover existing peers and add discovered peers to their local routing tables.

**Day 11 – FIND_NODE and Iterative Peer Lookup**

Implemented a TCP-based FIND_NODE client-server protocol that retrieves the closest known peers to a target node ID.

Developed an iterative lookup manager using XOR distance to identify closer peers, query multiple peers concurrently and progressively discover nodes across the network.

Added input validation, timeout handling, connection error handling and automated tests.

**Testing:** All 9 Day 11 tests passed. Full project test discovery completed successfully with 19 tests passing.

## Week 2 Achievements So Far

- 160-bit node identity generation and validation.
- XOR-based distance calculation.
- Peer information management and serialization.
- Kademlia-inspired routing table with 160 K-Buckets.
- Peer registration, refresh and replacement support.
- Closest-peer lookup.
- TCP bootstrap and dynamic node joining.
- FIND_NODE request-response protocol.
- Iterative peer lookup with concurrent queries.
- Automated testing of routing and discovery components.

## Upcoming Development

1. Implement CPU and RAM resource monitoring.
2. Develop asynchronous background resource gossip.
3. Exchange resource updates every 5 seconds.
4. Integrate DHT peer information with resource gossip.
5. Improve peer failure handling and routing reliability.
6. Test the integrated system across multiple nodes.

## Documentation

- [Day 1 – UDP Communication](day1_wk1/README.md)
- [Day 2 – TCP Communication](day2_wk1/README.md)
- [Day 3 – Peer Discovery and Task Management](day3_wk1/README.md)
- [Day 4 – Resource Monitoring and Distributed Execution](day4_wk1/README.md)
- [Day 5 – Persistence, Security and Monitoring](day5_wk1/README.md)
- [Day 6 – Recovery and Journal Integrity](day6_wk1/README.md)
- [Day 7 – Serialization and Remote Execution](day7_wk1/README.md)
- [Day 8 – DHT Foundation](day8_wk2/README.md)
- [Day 9 – Kademlia Routing Table](day9_wk2/README.md)
- [Day 10 – Bootstrap and Dynamic Node Joining](day10_wk2/README.md)
- [Day 11 – FIND_NODE and Iterative Lookup](day11_wk2/README.md)

## Current Limitations

- The bootstrap mechanism requires nodes to know an initial bootstrap server address.
- Peer health checks and automatic stale-peer removal need further integration with the DHT.
- Iterative lookup currently operates on known and discovered peers; broader network testing is still needed.
- Resource gossip integration with the new DHT is pending.
- Persistent node identity across restarts is not yet implemented.
- Larger-scale network testing and advanced failure recovery remain future improvements.
- Cloudpickle execution must be restricted to trusted peers because deserialization can execute code.

## Conclusion

MeshWeaver has evolved from basic network communication into a distributed task-processing system with remote execution, persistence, security and monitoring capabilities.

Week 2 extends the project toward decentralized networking through node identities, XOR-based routing, Kademlia-inspired K-Buckets, bootstrap-based joining and iterative peer lookup.

The next phase focuses on resource gossip and integrating decentralized discovery with load-aware task distribution.
