# MeshWeaver

## Project Overview

MeshWeaver is a Python-based peer-to-peer asynchronous task broker that enables multiple nodes to communicate, discover peers, exchange resource information, and distribute computational tasks without relying on centralized brokers such as Redis or RabbitMQ.

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

Python, Asyncio, UDP, TCP, JSON, Psutil, HMAC-SHA256, Cloudpickle, Base64, Secrets, Dataclasses, Streamlit, Unittest, Pytest, Git and GitHub.

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
| Day 12 | Resource monitoring, CPU/RAM status collection and report validation | Completed |
| Day 13 | Asynchronous background resource gossip with 5-second update intervals | Completed |
| Day 14 | DHT and gossip integration, multi-node testing and reliability improvements | Planned |

## Project Structure

```text
MeshWeaver/
│
├── day1_wk1/
├── day2_wk1/
├── day3_wk1/
├── day4_wk1/
├── day5_wk1/
│   ├── resource_monitor.py
│   ├── resource_gossip.py
│   ├── scheduler.py
│   ├── node.py
│   ├── test_resource_gossip_day12_13.py
│   └── README.md
│
├── day6_wk1/
├── day7_wk1/
├── day8_wk2/
├── day9_wk2/
├── day10_wk2/
├── day11_wk2/
│
├── .gitignore
├── README.md
└── requirements.txt
```

Each day folder contains its respective implementation, tests and README documentation where applicable. Resource gossip enhancements for Days 12 and 13 were implemented in the existing resource-monitoring and node modules.

## Current Progress

### Week 1 – Distributed Task Processing

Implemented asynchronous UDP and TCP communication, peer discovery, health monitoring, task queue management, resource monitoring, gossip, load-aware scheduling and remote task execution.

Added persistent task journaling, restart recovery, HMAC-SHA256 authentication, indirect peer discovery, terminal and web dashboards, and journal integrity auditing.

Implemented Python function serialization using Cloudpickle and Base64, enabling remote function execution between nodes.

Verified distributed execution using two local nodes, successfully forwarding and completing eight tasks.

### Week 2 – Decentralized Peer Discovery and Resource Management

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

**Testing:** All 9 Day 11 tests passed. Full project test discovery previously completed with 19 tests passing.

**Day 12 – Resource Monitoring and Report Validation**

Extended resource monitoring and resource gossip functionality to collect and exchange CPU utilization, RAM utilization and active task information.

Implemented resource report validation to reject invalid, stale, future-dated and older reports. Valid reports update the resource state and scheduler's peer-load information.

**Day 13 – Asynchronous Background Resource Gossip**

Implemented an asynchronous gossip engine that periodically exchanges resource reports with alive peers.

Added concurrent peer communication, acknowledgement and rejection handling, timeout management and graceful cancellation of the background gossip task during node shutdown.

**Testing:** Added focused resource gossip tests covering report validation, scheduler updates, peer communication acknowledgement and background task cancellation.

All 7 focused Day 12 and Day 13 tests passed.

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
- CPU and RAM resource monitoring.
- Resource report validation and stale-report handling.
- Scheduler updates using peer resource information.
- Asynchronous background resource gossip.
- Periodic resource exchange with alive peers.
- Timeout handling and graceful gossip cancellation.
- Focused automated testing for resource gossip.

## Upcoming Development

1. Integrate DHT peer discovery with the resource gossip mechanism.
2. Perform multi-node testing of resource exchange.
3. Improve peer failure handling and stale-peer removal.
4. Verify load-aware task distribution using updated resource information.
5. Improve routing reliability and recovery.
6. Explore larger-scale network testing and performance improvements.

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
- Resource gossip has been implemented and tested independently, but its complete integration with the new DHT requires further verification.
- Persistent node identity across restarts is not yet implemented.
- Larger-scale network testing and advanced failure recovery remain future improvements.
- Cloudpickle execution must be restricted to trusted peers because deserialization can execute code.

## Conclusion

MeshWeaver has evolved from basic network communication into a distributed task-processing system with remote execution, persistence, security and monitoring capabilities.

Week 2 extends the project toward decentralized networking through node identities, XOR-based routing, Kademlia-inspired K-Buckets, bootstrap-based joining and iterative peer lookup.

Resource monitoring and asynchronous resource gossip have now been implemented, bringing the project closer to decentralized, load-aware task distribution.

The next phase focuses on integrating DHT discovery with resource gossip, validating multi-node communication and improving overall network reliability.