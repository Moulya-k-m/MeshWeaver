# 🕸️ MeshWeaver
### Zero-Dependency P2P Async Task Broker

**Domain:** Distributed Systems & Edge Computing

MeshWeaver is a decentralized, peer-to-peer asynchronous task broker built using Python. It aims to distribute tasks across multiple nodes without depending on centralized message brokers such as Redis or RabbitMQ.

The project explores peer discovery, asynchronous communication, distributed resource monitoring, load-aware task scheduling, remote task execution, routing reliability, execution tracking, task analytics, node reliability monitoring and fault handling.

---

## 📌 Project Overview

Traditional task brokers often depend on centralized infrastructure to manage task distribution and communication. MeshWeaver explores an alternative approach in which independent nodes communicate directly and coordinate task processing.

Each node can participate in peer discovery, exchange resource information, evaluate peer availability and contribute to distributed task execution.

### 🎯 Key Objectives

- Build a decentralized peer-to-peer task broker.
- Enable asynchronous communication between nodes.
- Discover peers without relying entirely on a centralized registry.
- Exchange resource information between nodes.
- Support distributed task scheduling and execution.
- Monitor peer availability and handle node failures.
- Improve routing reliability through fallback mechanisms.
- Track task execution states and maintain persistent execution history.
- Analyse task performance and node-wise execution statistics.
- Monitor node reliability using historical execution outcomes.
- Minimize external dependencies using Python's asynchronous networking capabilities.

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

# 📅 Development Progress

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

### Week 3 – Routing Reliability and Distributed Execution

| Day | Focus | Status |
|---|---|---|
| Day 15 | Routing reliability and decision logging | Completed |
| Day 16 | Distributed execution tracking and persistent history | Completed |
| Day 17 | Task execution analytics and performance monitoring | Completed |
| Day 18 | Node reliability monitoring and health classification | Completed |
| Day 19 | Multi-node load balancing and stress testing | Upcoming |
| Day 20 | Integration, regression testing and documentation | Upcoming |

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

The work progressed towards a more integrated architecture, preparing the project for distributed peer discovery, serialization and routing functionality introduced in subsequent development.

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

Extended peer discovery functionality with lookup management and node lookup operations.

### Features

- Lookup manager.
- FIND_NODE functionality.
- Peer lookup operations.
- Routing table interaction.
- Discovery-related testing.

### Outcome

Established the foundation for locating nodes through distributed peer discovery and routing components.

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

## Day 14 – Cluster Integration and Reliability

Day 14 focused on validating the interaction between peer discovery, resource gossip, scheduler updates and peer failure handling.

The objective was to move beyond testing individual components and verify their behavior in a real multi-node environment.

### 🎯 Objectives

- Coordinate peer discovery with resource gossip.
- Register discovered peers in the peer table.
- Exchange authenticated resource reports.
- Update scheduler load information.
- Detect unavailable peers.
- Remove stale resource information.
- Validate the system using a real three-node environment.

### 1. Discovery and Gossip Integration

Created an integration coordinator to connect the peer discovery component with resource gossip.

Implemented functionality for:

- Discovering and registering peers.
- Refreshing peer information.
- Excluding the bootstrap server from regular gossip communication.
- Starting and stopping the gossip process.
- Coordinating peer information with resource gossip.

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

### Day 14 Test Results

| Functionality | Result |
|---|---|
| Three-node peer discovery | PASS |
| Signed resource gossip exchange | PASS |
| Scheduler load report updates | PASS |
| Failed peer detection | PASS |
| Dead-peer resource cleanup | PASS |

### Regression Testing

| Test Module | Passed |
|---|---:|
| Day 14 integration tests | 3 |
| Day 12–13 resource gossip | 7 |
| Day 10 discovery | 4 |
| Day 11 lookup manager | 5 |
| Day 11 FIND_NODE | 4 |
| **Total** | **23** |

**Final verified result: 23 passed in 10.90 seconds.**

### Outcome

Validated peer discovery, authenticated resource exchange, scheduler updates and peer failure handling through integration and regression testing.

---

# 🧭 Week 3 – Routing Reliability and Distributed Execution

## Day 15 – Routing Reliability and Decision Transparency

Day 15 focused on improving routing reliability and making task scheduling decisions easier to understand and debug.

The objective was to ensure that stale peer information is not used for routing and that tasks can still be processed locally when forwarding to another peer fails.

### 🎯 Objectives

- Validate peer load report freshness.
- Prevent routing decisions based on stale resource information.
- Handle failed task forwarding.
- Provide local execution fallback.
- Record routing decisions for debugging and monitoring.

### 1. Stale Peer Load Report Handling

Added and tested routing behavior that ignores outdated peer load reports.

This prevents the scheduler from selecting peers based on old resource information.

### 2. Failed Forwarding and Local Fallback

Validated the behavior when a selected peer becomes unavailable during task forwarding.

Implemented and tested the fallback behavior:

- Attempt forwarding to the selected peer.
- Handle forwarding failure.
- Retain the task locally.
- Return a successful task acceptance response.
- Record the local execution decision.

### 3. Routing Decision Logger

Introduced `RoutingDecisionLogger` to maintain structured routing decision records in JSON Lines format.

Each record contains:

- Timestamp.
- Task ID.
- Node ID.
- Routing decision.
- Reason for the decision.
- Local load score.
- Selected peer ID.
- Selected peer load score.

The logger records decisions such as:

- `FORWARDED` – Task successfully forwarded to another peer.
- `LOCAL` – Task retained for local processing.

### 4. Day 15 Testing

| Test Case | Result |
|---|---|
| Scheduler ignores stale load reports | PASS |
| Failed forwarding falls back to local queue | PASS |
| Structured routing log generation | VERIFIED |

### Latest Test Output

```text
pytest day15_wk3 -v

collected 2 items

test_failed_forwarding_falls_back_to_local_queue PASSED
test_scheduler_ignores_stale_load_report PASSED

2 passed in 0.13s
```

The generated JSONL log was also inspected and verified to contain the local fallback decision, task identifier, reason and load information.

### Outcome

Improved routing transparency and reliability by adding structured decision logging, stale-report validation and local fallback behavior when peer forwarding fails.

---

## Day 16 – Distributed Execution Tracking and Persistent History

Day 16 focused on introducing a dedicated execution tracking mechanism to monitor the lifecycle of distributed tasks.

The objective was to maintain task execution states, record important execution events and preserve task history across application restarts.

### 🎯 Objectives

- Track the lifecycle of individual tasks.
- Generate unique task identifiers.
- Record task submission, assignment, completion and failure.
- Maintain persistent execution history.
- Restore task states after restarting the application.
- Validate task tracking and history recovery.

### 1. Execution Tracker

Implemented an `ExecutionTracker` class to maintain the latest state of each tracked task.

Supported task states:

- `SUBMITTED`
- `ASSIGNED`
- `COMPLETED`
- `FAILED`

### 2. Task Lifecycle Management

Implemented methods for:

- `submit()` – Generates a unique task ID and records submission.
- `assign()` – Records the node assigned to a task.
- `complete()` – Records successful task completion and its result.
- `fail()` – Records task failure and the associated error.
- `get_status()` – Retrieves the current task state.
- `get_task()` – Retrieves task information.
- `get_all_tasks()` – Returns tracked task states.

### 3. Persistent Execution History

Introduced JSONL-based execution history storage.

Each event records:

- Task ID.
- Execution status.
- Node information.
- Task result.
- Error information.
- UTC timestamp.

This allows task execution events to be stored independently of the application's in-memory state.

### 4. History Restoration

Implemented `load_history()` to restore task information from the persistent JSONL file.

Features include:

- Reading previously recorded execution events.
- Reconstructing the latest state of each task.
- Skipping corrupted JSON entries.
- Preserving task history across application restarts.

### 5. Task State Validation

Added validation to prevent:

- Operations on unknown task IDs.
- Reassigning completed tasks.
- Modifying tasks that have already reached a terminal state.

### Day 16 Outcome

Established a persistent task execution tracking foundation that records task lifecycle events and supports state restoration after application restarts.

---

## Day 17 – Distributed Task Execution Analytics

Day 17 focused on extending the execution tracking mechanism developed on Day 16 with a separate analytics module.

The objective was to analyse persistent task execution history and generate useful insights into task completion, failure rates, node-level execution distribution and average execution time.

### 🎯 Objectives

- Analyse historical task execution events.
- Calculate overall task execution statistics.
- Identify completed, failed and pending tasks.
- Calculate task execution success rates.
- Generate node-wise execution statistics.
- Calculate average task execution time.
- Handle corrupted and missing execution history.
- Provide a terminal-based analytics interface.

### 1. Task Execution Analytics Module

Developed a separate `TaskAnalytics` class to process execution history generated by the Day 16 Execution Tracker.

The analytics module reads JSONL records independently without modifying the existing execution tracker.

### 2. Execution History Loading

Implemented `load_events()` to retrieve execution records from the persistent history file.

Features include:

- JSONL event loading.
- Validation of essential event fields.
- Handling missing history files.
- Skipping malformed JSON entries.
- Maintaining a separate collection of loaded execution events.

### 3. Task Summary Analytics

Implemented `get_summary()` to calculate overall execution statistics.

The summary includes:

- Total number of unique tasks.
- Completed tasks.
- Failed tasks.
- Pending tasks.
- Overall execution success rate.

The success rate is calculated using completed and failed tasks:

```text
Success Rate = (Completed Tasks / Finished Tasks) × 100
```

Pending tasks are excluded from the success-rate calculation.

### 4. Node-wise Execution Statistics

Implemented `get_node_statistics()` to analyse task distribution across individual nodes.

The module tracks:

- Number of completed tasks per node.
- Number of failed tasks per node.
- Number of tasks remaining in other execution states.

This provides visibility into the recorded task outcomes associated with individual nodes.

### 5. Average Execution Time Analysis

Implemented `get_average_execution_time()` to calculate the average time between task submission and its terminal execution event.

The calculation considers:

- Initial task submission timestamp.
- Final completion or failure timestamp.
- Multiple execution events belonging to the same task.
- Both successful and failed task executions.

Tasks without valid submission and terminal timestamps are excluded from the calculation.

### 6. Terminal Analytics Runner

Created `run_analytics.py` to display execution analytics directly in the terminal.

The runner displays:

- Total tasks.
- Completed tasks.
- Failed tasks.
- Pending tasks.
- Success rate.
- Node-wise execution statistics.
- Average execution time.

It also handles empty or unavailable execution history without terminating unexpectedly.

### 7. Automated Testing

Created a dedicated pytest test suite covering the analytics implementation.

| Test Case | Result |
|---|---|
| Execution event loading | PASS |
| Task summary calculation | PASS |
| Node-wise statistics | PASS |
| Average execution time | PASS |
| Empty history handling | PASS |
| Corrupted history handling | PASS |
| Missing history file handling | PASS |
| Failed task execution-time calculation | PASS |

**Final verified result: 8 passed in 0.17 seconds.**

### Files Created

| File | Description |
|---|---|
| `task_analytics.py` | Core task analytics implementation |
| `test_task_analytics.py` | Automated analytics test suite |
| `run_analytics.py` | Terminal-based analytics runner |

### Outcome

Successfully developed an independent task execution analytics module that extends MeshWeaver's monitoring capabilities.

The implementation provides visibility into task completion, execution failures, node-wise task distribution and average execution time.

It also establishes a foundation for future performance monitoring, workload analysis and distributed execution optimization.

---

## Day 18 – Node Reliability Monitoring and Health Classification

Day 18 focused on analysing node-wise task execution outcomes to evaluate the reliability and health of individual MeshWeaver nodes.

The objective was to use historical execution records to identify reliable nodes, detect nodes with frequent failures and avoid making reliability judgements when insufficient task data is available.

### 🎯 Objectives

- Calculate node-wise task success and failure rates.
- Analyse completed and failed tasks for individual nodes.
- Measure average node execution time.
- Classify node health based on reliability.
- Identify nodes with insufficient execution data.
- Rank nodes according to their reliability.
- Handle missing and corrupted execution history.
- Provide a terminal-based node reliability report.

### 1. Node Reliability Module

Developed a separate `NodeReliability` class to analyse execution history generated by the Day 16 Execution Tracker.

The module processes JSONL execution records independently without modifying the existing tracker.

### 2. Node Reliability Calculation

Implemented `get_node_reliability()` to calculate the reliability statistics of individual nodes.

The module tracks:

- Total tasks handled by each node.
- Successfully completed tasks.
- Failed tasks.
- Task success rate.
- Task failure rate.

### 3. Node Execution Time Analysis

Implemented `get_node_execution_times()` to calculate average execution time for individual nodes.

The calculation considers task submission timestamps and the final completion or failure event.

### 4. Node Health Classification

Implemented `get_node_health()` to classify nodes based on their success rates and minimum task requirements.

Supported health classifications:

| Health Status | Condition |
|---|---|
| HEALTHY | Success rate greater than or equal to 90% |
| WARNING | Success rate greater than or equal to 70% but below 90% |
| CRITICAL | Success rate below 70% |
| INSUFFICIENT_DATA | Fewer than 5 recorded tasks |

The minimum task requirement prevents a node from receiving a confident health classification based on very limited execution history.

### 5. Node Performance Ranking

Implemented `get_ranked_nodes()` to rank nodes based on:

- Higher task success rate.
- Total number of recorded tasks as a secondary ranking factor.

This provides a simple comparison of node reliability using historical task outcomes.

### 6. Demonstration History Generator

Created `generate_demo_history.py` to generate an isolated sample execution history using the existing Day 16 Execution Tracker.

The demonstration contains 16 tasks across four nodes:

| Node | Completed | Failed | Success Rate |
|---|---:|---:|---:|
| node-A | 5 | 0 | 100% |
| node-B | 4 | 1 | 80% |
| node-C | 2 | 3 | 40% |
| node-D | 1 | 0 | 100% |

This sample data allows different health classifications to be tested without modifying the actual Day 16 execution history.

### 7. Terminal Reliability Report

Created `run_reliability.py` to display:

- Number of execution events loaded.
- Node-wise completed and failed tasks.
- Success and failure rates.
- Average node execution times.
- Node health classifications.
- Node performance rankings.

The runner also supports a custom JSONL history-file path.

### 8. Automated Testing

Created a dedicated pytest test suite covering:

| Test Case | Result |
|---|---|
| Execution event loading | PASS |
| Node reliability calculation | PASS |
| Node execution time calculation | PASS |
| Node health classification | PASS |
| Node performance ranking | PASS |
| Missing history file handling | PASS |
| Corrupted history handling | PASS |
| Invalid minimum task requirement | PASS |

**Final verified result: 8 passed in 0.30 seconds.**

### 9. Demonstration Results

Successfully generated and analysed 16 sample tasks, producing 48 execution events.

Verified node health classifications:

| Node | Success Rate | Health |
|---|---:|---|
| node-A | 100% | HEALTHY |
| node-B | 80% | WARNING |
| node-C | 40% | CRITICAL |
| node-D | 100% | INSUFFICIENT_DATA |

The results confirmed that the reliability monitor correctly distinguishes between healthy, warning and critical nodes while accounting for insufficient execution data.

### Files Created

| File | Description |
|---|---|
| `node_reliability.py` | Core node reliability calculations |
| `test_node_reliability.py` | Automated reliability test suite |
| `run_reliability.py` | Terminal-based reliability report |
| `generate_demo_history.py` | Isolated demonstration history generator |

### Day 18 Outcome

Successfully developed a node reliability monitoring module that evaluates historical task outcomes, calculates node-wise reliability metrics, classifies node health and ranks nodes based on execution performance.

The module extends MeshWeaver's monitoring capabilities beyond task-level analytics towards node-level reliability analysis.

**Note:** Demonstration results use generated sample execution events. Integration with live distributed node execution remains future work.

---

# 📁 Project Structure

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
│   ├── test_real_cluster.py
│   └── README.md
│
├── day15_wk3/
│   ├── routing_logger.py
│   ├── test_routing_reliability.py
│   ├── routing_logs/
│   └── README.md
│
├── day16_wk3/
│   ├── execution_tracker.py
│   ├── test_execution_tracker.py
│   └── README.md
│
├── day17_wk3/
│   ├── task_analytics.py
│   ├── test_task_analytics.py
│   ├── run_analytics.py
│   └── README.md
│
├── day18_wk3/
│   ├── node_reliability.py
│   ├── test_node_reliability.py
│   ├── run_reliability.py
│   ├── generate_demo_history.py
│   └── README.md
│
├── .gitignore
├── README.md
└── requirements.txt
```

Each development folder contains its respective implementation, tests and documentation where applicable.

Days 12 and 13 extend the existing resource monitoring and gossip implementation in `day5_wk1`, with additional focused tests and separate documentation.

Day 14 introduces discovery and gossip integration coordination, integration tests and real multi-node cluster testing in `day14_wk2`.

Day 15 introduces routing reliability tests and structured routing decision logging in `day15_wk3`, with the logger integrated into the existing `day5_wk1/node.py` runtime.

Day 16 introduces dedicated task lifecycle tracking and persistent execution history.

Day 17 introduces independent task analytics based on the execution history generated by Day 16.

Day 18 introduces independent node reliability analysis using historical execution outcomes.

---

# 🧪 Running Tests

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

Run the Day 15 routing reliability tests:

```bash
pytest day15_wk3 -v
```

Run the Day 16 execution tracker tests:

```bash
pytest day16_wk3 -v
```

Run the Day 17 analytics tests:

```bash
pytest day17_wk3 -v
```

Run the Day 17 analytics runner:

```bash
python day17_wk3/run_analytics.py
```

Run the Day 18 node reliability tests:

```bash
pytest day18_wk3/test_node_reliability.py -v
```

Generate isolated Day 18 demonstration history:

```bash
python day18_wk3/generate_demo_history.py
```

Run the Day 18 reliability report:

```bash
python day18_wk3/run_reliability.py day18_wk3/demo_execution_history.jsonl
```

Run the combined Week 2 regression suite:

```bash
pytest day14_wk2 day5_wk1/test_resource_gossip_day12_13.py day10_wk2/test_discovery.py day11_wk2/test_lookup_manager.py day11_wk2/test_find_node.py -v
```

---

## Latest Verified Test Results

| Test Suite | Verified Result |
|---|---:|
| Week 2 combined regression suite | 23 passed |
| Day 14 integration tests | 3 passed |
| Day 15 routing reliability tests | 2 passed |
| Day 17 task analytics tests | 8 passed |
| Day 18 node reliability tests | 8 passed |

**Day 18 latest test execution:**

```text
8 passed in 0.30s
```

**Day 18 demonstration execution:**

```text
Execution events loaded: 48

node-A: HEALTHY (100.0% success)
node-B: WARNING (80.0% success)
node-C: CRITICAL (40.0% success)
node-D: INSUFFICIENT_DATA (100.0% success)
```

*Note: These results represent separate verified test runs, not one combined execution. Day 16 test results should be added after its dedicated test execution.*

---

# 🏆 Achievements So Far

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
- Implemented remote function serialization and execution foundations.
- Audited discovery and authenticated TCP connectivity across a 10-node local test cluster.
- Added routing decision logging.
- Implemented and tested local fallback when peer forwarding fails.
- Developed task lifecycle tracking with unique task identifiers.
- Implemented persistent JSONL execution history.
- Added task state restoration after application restart.
- Developed task execution summary analytics.
- Implemented node-wise execution statistics.
- Added average task execution-time calculations.
- Created a terminal-based analytics runner.
- Developed node reliability monitoring and health classification.
- Implemented node-wise success and failure rate calculations.
- Added node execution-time analysis and performance ranking.
- Successfully passed 23 Week 2 regression tests, 2 Day 15 reliability tests, 8 Day 17 analytics tests and 8 Day 18 reliability tests.

---

# ⚠️ Current Limitations

- The newer TCP-based DHT discovery components and the existing Node runtime's UDP discovery mechanism are still separate.
- The Day 14 integration coordinator is not yet wired into the main `Node.run()` lifecycle.
- Large-scale cluster testing is still pending.
- More extensive testing is needed for simultaneous node failures and task recovery.
- Further validation is required for distributed task execution under changing network conditions.
- Cloudpickle deserialization can execute code and should be restricted to trusted peers.
- Routing decision logging has been validated with focused tests; broader multi-node routing observability remains future work.
- Day 16 execution tracking currently maintains its in-memory state and persistent JSONL event history; further integration with the complete distributed execution pipeline is required.
- Day 17 analytics currently reads the execution history file independently. Actual analytics require recorded execution events in that file.
- Day 18 reliability monitoring currently analyses historical execution events independently. Live node reliability monitoring requires integration with the distributed execution pipeline.
- Day 18 demonstration results use generated sample data and should not be interpreted as live cluster measurements.
- End-to-end execution and failure recovery require further integration and validation.

---

# 🔮 Upcoming Development

The next development phase will focus on:

- Implementing task failure recovery and reassignment.
- Integrating execution tracking with the distributed task processing pipeline.
- Improving distributed task routing.
- Strengthening load-aware scheduling.
- Improving node-level workload distribution.
- Testing larger peer networks.
- Introducing multi-node stress testing.
- Improving security and communication reliability.
- Expanding execution analytics with additional performance metrics.
- Integrating node reliability monitoring with live execution.
- Validating the complete end-to-end task broker workflow.

---

# 👥 Development

**Project:** MeshWeaver  
**Domain:** Distributed Systems & Edge Computing  
**Implementation Language:** Python  
**Architecture:** Decentralized Peer-to-Peer  
**Development Branch:** `Navya`

---

# 📌 Conclusion

MeshWeaver is an ongoing exploration of decentralized task processing using Python's asynchronous networking capabilities.

Across the first 18 development days, the project has progressed from basic UDP and TCP communication to peer discovery, routing foundations, resource gossip, scheduler integration, multi-node reliability testing, routing decision transparency, persistent task execution tracking, task execution analytics and node reliability monitoring.

The implementation explores how independent nodes can communicate, exchange resource information, monitor peer availability, make load-aware routing decisions, respond to forwarding failures and maintain visibility into task and node performance without relying on a traditional centralized message broker.

With successful Week 2 regression testing, Day 15 routing reliability tests, Day 17 analytics testing and Day 18 node reliability testing, MeshWeaver has established a foundation for further development towards a reliable peer-to-peer asynchronous task broker.

**Smart Routing. Distributed Execution. Decentralized Coordination.**
