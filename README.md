# 🕸️ MeshWeaver
### Zero-Dependency P2P Async Task Broker

**Distributed Systems & Edge Computing**

MeshWeaver is a decentralized, peer-to-peer asynchronous task broker built using Python. It aims to distribute tasks across multiple nodes without depending on a centralized message broker such as Redis or RabbitMQ.

The system explores peer discovery, asynchronous communication, distributed resource monitoring, load-aware task scheduling and fault handling.

---

## 📌 Project Overview

Traditional task brokers often depend on centralized infrastructure to manage task distribution and communication. MeshWeaver explores an alternative approach in which independent nodes communicate directly and coordinate task processing.

Each node can participate in peer discovery, exchange resource information and contribute to distributed task execution.

### 🎯 Key Objectives

- Build a decentralized peer-to-peer task broker.
- Enable asynchronous communication between nodes.
- Discover peers without relying entirely on a centralized registry.
- Exchange resource information between nodes.
- Support distributed task scheduling.
- Monitor peer availability and handle node failures.
- Minimize external dependencies by using Python's built-in asynchronous networking capabilities.

---

## 🛠️ Technology Stack

| Technology | Purpose |
|---|---|
| Python | Core implementation |
| Asyncio | Asynchronous communication and task management |
| UDP | Peer discovery and announcements |
| TCP | Reliable communication and message exchange |
| JSON | Structured message exchange |
| Cloudpickle | Python object and function serialization |
| HMAC-SHA256 | Message authentication |
| SHA-1 | Node identifier generation |
| Pytest | Unit and integration testing |
| Git & GitHub | Version control and collaboration |

---

## 📅 Development Progress

### Week 1 – Communication and Core Foundations

| Day | Focus | Status |
|---|---|---|
| Day 1 | UDP communication – listener, sender and PING/PONG | Completed |
| Day 2 | TCP communication and message framing | Completed |
| Day 3 | Continued core communication development | Completed |
| Day 4 | Core node and communication development | Completed |
| Day 5 | Node integration and resource monitoring foundations | Completed |
| Day 6 | Continued system integration and development | Completed |
| Day 7 | Week 1 development and documentation | Completed |

### Week 2 – Peer Discovery and Distributed Coordination

| Day | Focus | Status |
|---|---|---|
| Day 8 | Node identity and peer information | Completed |
| Day 9 | Peer representation and routing table | Completed |
| Day 10 | Bootstrap server and peer discovery | Completed |
| Day 11 | Lookup manager and FIND_NODE functionality | Completed |
| Days 12–13 | Resource gossip and asynchronous resource exchange | Completed |
| Day 14 | Cluster integration, reliability and failure recovery testing | Completed |

---

# 🚀 Week 1 – Communication and Core Foundations

## Day 1 – UDP Communication

Implemented the initial communication mechanism between independent MeshWeaver nodes using UDP.

### Features Implemented

- UDP listener and sender.
- PING/PONG message exchange.
- JSON-based message format.
- Unique node identifier generation using UUID and SHA-1.
- Configurable message count and timeout.
- Round-trip time measurement.
- Minimum, average and maximum RTT statistics.
- Dropped malformed packet handling.

### Outcome

Established the initial communication foundation required for peer-to-peer networking.

## Day 2 – TCP Communication and Message Framing

Implemented reliable TCP communication with message framing between client and server.

### Features Implemented

- TCP client and server.
- Four-byte big-endian message length prefix.
- Message size validation with a 1 MB maximum.
- Structured JSON message exchange.
- HELLO and HELLO_ACK communication.
- ADD operation for arithmetic requests.
- TIME operation for UTC timestamp responses.
- Unknown operation handling.

### Outcome

Established structured TCP communication and message framing to support reliable data exchange between nodes.

## Days 3–4 – Core Development

Continued development of the foundational networking and node components.

The focus was on progressing from individual communication scripts towards a more organized node-based architecture.

### Development Focus

- Organizing communication components.
- Developing reusable node functionality.
- Preparing the system for asynchronous coordination.
- Building foundations for distributed communication.

## Day 5 – Node Integration and Resource Monitoring

Progressed towards integrating individual components into the MeshWeaver node architecture.

### Development Focus

- Node initialization and communication.
- Peer table management.
- Resource monitoring.
- Scheduler integration.
- Task storage and processing foundations.
- Resource gossip implementation and supporting tests.

The `day5_wk1` directory contains several components that were subsequently extended and tested during later development.

### Outcome

Established important foundations for integrating resource monitoring, peer management and task coordination.

## Days 6–7 – Continued Core Development

Continued developing and organizing the core MeshWeaver components.

The work progressed towards a more integrated architecture, preparing the project for the distributed peer discovery and routing functionality introduced in Week 2.

---

# 🌐 Week 2 – Peer Discovery and Distributed Coordination

## Day 8 – Node Identity and Peer Information

Introduced the foundation for identifying nodes and maintaining peer information.

### Development Focus

- Node identity.
- Peer information representation.
- Node-related metadata.
- Foundations for distributed peer management.

## Day 9 – Peer Representation and Routing Table

Implemented peer representation and routing table foundations.

### Features

- Peer data representation.
- Routing table implementation.
- Peer information management.
- Support for organizing discovered nodes.
- Foundations for Kademlia-style peer routing.

### Outcome

Established the routing structures required for decentralized peer discovery.

## Day 10 – Bootstrap Server and Peer Discovery

Implemented bootstrap-based peer discovery to help nodes identify and connect with other available nodes.

### Features

- Bootstrap server.
- Peer discovery mechanism.
- Node registration and peer information exchange.
- TCP-based communication with the bootstrap server.
- Peer discovery management.

### Outcome

Enabled nodes to obtain peer information through the bootstrap mechanism.

## Day 11 – Lookup Manager and FIND_NODE

Extended the peer discovery functionality with lookup management and node lookup operations.

### Features

- Lookup manager.
- FIND_NODE functionality.
- Peer lookup operations.
- Routing table interaction.
- Discovery-related testing.

### Outcome

Established the foundation for locating nodes through the distributed peer discovery and routing components.

## Days 12–13 – Resource Gossip and Asynchronous Exchange

Focused on exchanging resource information between available MeshWeaver nodes.

The existing resource gossip implementation was extended and tested under `day5_wk1`.

### Features

- Resource report generation.
- CPU utilization monitoring.
- RAM utilization monitoring.
- Active task count reporting.
- Timestamp-based report validation.
- Stale report rejection.
- Resource information exchange between peers.
- Scheduler load report updates.
- Peer resource state management.
- Asynchronous gossip loop.
- Removal of outdated peer resource information.

### Resource Report Validation

Incoming resource reports are checked for:

- Required report fields.
- Valid resource values.
- Valid timestamps.
- Stale report age.
- Invalid or outdated information.

### Outcome

Enabled nodes to exchange resource information and maintain updated peer load information for distributed scheduling.

---

# 🔗 Day 14 – Cluster Integration and Reliability

Day 14 focused on validating the interaction between peer discovery, resource gossip, scheduler updates and peer failure handling.

The objective was to move beyond testing individual components and verify their behavior in a real multi-node environment.

## 🎯 Objectives

- Coordinate peer discovery with resource gossip.
- Register discovered peers in the peer table.
- Exchange authenticated resource reports.
- Update scheduler load information.
- Detect unavailable peers.
- Remove stale resource information.
- Validate the system using a real three-node cluster.

## Implementation

### 1. Discovery and Gossip Integration

Created an integration coordinator to connect the newer peer discovery component with resource gossip.

Implemented functionality for:

- Discovering and registering peers.
- Refreshing peer information.
- Excluding the bootstrap server from regular gossip communication.
- Starting and stopping the gossip process.
- Coordinating peer information with the resource gossip component.

### 2. Resource Exchange Validation

Validated resource exchange through the existing TCP communication mechanism.

Nodes exchange authenticated resource reports containing CPU, RAM and active task information.

### 3. Peer Failure Recovery

Improved the existing node reaper mechanism.

When a peer becomes DEAD:

- Its resource state is removed.
- Its last update timestamp is cleared.
- Its scheduler load report is removed.
- Outdated resource information is prevented from being reused.

### 4. Real Three-Node Cluster Testing

Created a real integration test using three independent MeshWeaver nodes.

The test validates:

1. Starting three nodes.
2. Discovering peers through UDP announcements.
3. Exchanging signed resource reports over TCP.
4. Updating scheduler load reports.
5. Stopping one node.
6. Detecting the failed peer.
7. Cleaning up its resource information.
8. Gracefully shutting down the remaining nodes.

## Day 14 Test Results

| Functionality | Result |
|---|---|
| Three-node peer discovery | PASS |
| Signed resource gossip exchange | PASS |
| Scheduler load report updates | PASS |
| Failed peer detection | PASS |
| Dead-peer resource cleanup | PASS |

### Regression Testing

The combined regression suite covered Day 14, resource gossip, peer discovery, lookup management and FIND_NODE.

| Test Module | Passed |
|---|---:|
| Day 14 integration tests | 3 |
| Day 12–13 resource gossip | 7 |
| Day 10 discovery | 4 |
| Day 11 lookup manager | 5 |
| Day 11 FIND_NODE | 4 |
| **Total** | **23** |

**Final result: 23 passed in 10.90 seconds.**

---
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
│   ├── test_resource_gossip_day12_13.py
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
├── day12_day13_wk2/
│   └── README.md
│
├── day14_wk2/
│   ├── __init__.py
│   ├── integration.py
│   ├── test_integration.py
│   └── test_real_cluster.py
│
├── .gitignore
├── README.md
└── requirements.txt
```

Each day folder contains its respective implementation, tests and README documentation where applicable.

Days 12 and 13 extend the existing resource monitoring and gossip implementation in `day5_wk1`, with additional focused tests and separate documentation in `day12_day13_wk2`.

Day 14 introduces discovery and gossip integration coordination, integration tests and real multi-node cluster testing in `day14_wk2`. The existing node failure cleanup improvement is maintained in `day5_wk1/node.py`.

---

## 🧪 Running Tests

Install the project dependencies:

```bash
pip install -r requirements.txt
```

Run the Day 14 tests:

```bash
pytest day14_wk2 -v
```

Run the real cluster integration test:

```bash
pytest day14_wk2/test_real_cluster.py -v -s
```

Run the combined regression suite:

```bash
pytest day14_wk2 day5_wk1/test_resource_gossip_day12_13.py day10_wk2/test_discovery.py day11_wk2/test_lookup_manager.py day11_wk2/test_find_node.py -v
```

### Latest Verified Test Result

```text
23 passed in 10.90s
```

---

## 🏆 Achievements So Far

- Implemented UDP-based node communication.
- Established TCP communication with message framing.
- Developed foundational node and peer management components.
- Implemented node identity and peer representation.
- Developed routing table and lookup functionality.
- Implemented bootstrap-based peer discovery.
- Developed resource monitoring and gossip mechanisms.
- Added authenticated resource report exchange.
- Integrated scheduler load updates.
- Improved dead-peer resource cleanup.
- Validated communication using a real three-node cluster.
- Successfully passed 23 combined regression tests.

---

## ⚠️ Current Limitations

- The newer TCP-based DHT discovery components and the existing Node runtime's UDP discovery mechanism are still separate.
- The Day 14 integration coordinator is not yet wired into the main `Node.run()` lifecycle.
- Large-scale cluster testing is still pending.
- More extensive testing is needed for simultaneous node failures and task recovery.
- Further validation is required for distributed task execution under changing network conditions.
- Cloudpickle execution should be restricted to trusted peers.

---

## 🔮 Upcoming Development

The next development phase can focus on:

- Integrating the newer DHT discovery mechanism into the main node runtime.
- Improving distributed task routing.
- Implementing and validating task execution across multiple nodes.
- Strengthening failure recovery and task requeue mechanisms.
- Improving load-aware scheduling.
- Testing larger peer networks.
- Improving security and communication reliability.
- Validating the complete end-to-end task broker workflow.

---

## 👥 Development

**Project:** MeshWeaver  
**Domain:** Distributed Systems & Edge Computing  
**Implementation Language:** Python  
**Architecture:** Decentralized Peer-to-Peer  
**Development Branch:** `Navya`

---

## 📌 Conclusion

MeshWeaver is an ongoing exploration of decentralized task processing using Python's asynchronous networking capabilities.

Across the first 14 development days, the project has progressed from basic UDP and TCP communication to peer discovery, routing foundations, resource gossip, scheduler integration and multi-node reliability testing.

The implementation demonstrates how independent nodes can communicate, exchange resource information, monitor peer availability and respond to node failures without relying on a traditional centralized message broker.

With 23 regression tests passing, the project has established a foundation for further development towards a reliable and scalable peer-to-peer asynchronous task broker.