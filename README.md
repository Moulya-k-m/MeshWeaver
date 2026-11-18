# MeshWeaver

## Project Overview

MeshWeaver is a Python-based peer-to-peer asynchronous task broker designed to allow multiple nodes to communicate, exchange information, monitor resources, and distribute computational tasks efficiently.

The project explores asynchronous networking, peer discovery, node health monitoring, resource sharing, load-aware scheduling, distributed task execution, function serialization, persistent task recovery, message authentication, system monitoring, journal integrity auditing, and decentralized peer discovery mechanisms.

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
- Implement XOR-based node distance calculation.
- Develop Kademlia-inspired routing tables and peer lookup mechanisms.

## Technology Stack

- Python
- Asyncio
- UDP and TCP networking
- JSON message framing
- Psutil for system resource monitoring
- HMAC-SHA256 for message authentication
- Cloudpickle for Python function serialization
- Base64 for encoded serialized data
- Secrets for secure random node identity generation
- Dataclasses for peer information management
- JSON for peer information serialization
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

## Week 2 Progress

| Day | Work | Status |
|---|---|---|
| Day 8 | DHT foundation, 160-bit node identity generation, XOR distance calculation, peer information management and JSON serialization | Completed |
| Day 9 | Advanced Kademlia routing table, K-Bucket implementation, peer management and closest-peer lookup | Completed |
| Day 10 | Bootstrap mechanism and dynamic node joining | Planned |
| Day 11 | Iterative peer lookup and node discovery | Planned |
| Day 12 | Gossip resource monitoring and CPU/RAM status collection | Planned |
| Day 13 | Asynchronous background gossip tasks with 5-second resource updates | Planned |
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

### Day 8 – DHT Foundation, Node Identity and Peer Information Management

Established the foundation for implementing a lightweight Kademlia-inspired Distributed Hash Table (DHT) in MeshWeaver.

Implemented unique 160-bit node identifier generation using Python's `secrets` module. Each node identifier is represented as a 40-character hexadecimal string.

Added node ID validation to verify the correct hexadecimal format and identifier length before using node identities in distance calculations and peer records.

Implemented XOR-based distance calculation between two node identifiers using Python's bitwise XOR operator. This provides the mathematical foundation for organizing peers within the Kademlia identifier space.

Developed a `PeerInfo` dataclass to store peer information, including:

- Unique node ID.
- IP address.
- Communication port.
- Last-seen timestamp.

Added peer validation to reject invalid node identifiers, empty IP address values, and port numbers outside the valid range.

Implemented peer activity timestamp updates to record the latest observed activity of a peer.

Introduced peer information serialization using JSON-compatible dictionaries. The `to_dict()` method converts peer records into transferable dictionary representations, while the `from_dict()` class method reconstructs PeerInfo objects from received dictionary data.

Created dedicated integration, edge-case and serialization tests to verify the implemented components.

**Testing and Verification:**

- Verified successful generation and validation of 160-bit node identities.
- Tested XOR distance calculation using predefined node IDs.
- Verified that identical node IDs produce zero XOR distance.
- Tested XOR symmetry and non-negative distance properties.
- Verified that different node IDs produce non-zero distance.
- Tested rejection of invalid node IDs and invalid peer ports.
- Verified peer information creation and timestamp updates.
- Tested integration between node identity generation, XOR distance calculation and peer management.
- Verified JSON serialization and deserialization of peer information.

The integration test completed successfully.

All 9 edge-case and XOR property tests passed.

Serialization and deserialization tests passed, confirming that the reconstructed peer information preserved its original values.

**Result:** Day 8 successfully established the node identity, XOR distance and peer information foundation required for the upcoming Kademlia routing implementation.

Actual DHT routing tables, dynamic node joining and network-level peer lookup remained planned for subsequent milestones.

### Day 9 – Advanced Kademlia Routing Table and Peer Management

Extended the Day 8 DHT foundation by implementing an advanced Kademlia-inspired routing table for MeshWeaver.

Implemented node ID validation and SHA-1-based 160-bit node identity generation for routing table operations and testing.

Developed XOR-based distance calculation to determine the logical distance between the local node and other peer identities.

Implemented the K-Bucket data structure to organize known peers according to their XOR distance from the local node.

Created a routing table containing 160 K-Buckets corresponding to the 160-bit node identifier space.

Developed a reusable `Peer` dataclass to store peer information, including:

- Unique 160-bit node ID.
- IP address.
- Communication port.
- Last-seen timestamp.

Added peer validation during object creation to ensure valid node IDs, non-empty IP addresses and port numbers within the range of 1–65535.

Implemented peer activity timestamp updates and dictionary-based peer information representation.

**K-Bucket Management:**

- Implemented configurable bucket capacity.
- Added peer insertion and removal operations.
- Prevented duplicate peer entries.
- Refreshed existing peers when they were encountered again.
- Maintained peer ordering based on recent activity.
- Handled full-bucket conditions.

**Routing Table Management:**

- Created 160 routing buckets for each local node.
- Calculated XOR distance between local and remote node identities.
- Determined the appropriate bucket using the highest set bit of the XOR distance.
- Registered peers in their corresponding buckets.
- Prevented the local node from being added to its own routing table.
- Maintained peer information across multiple buckets.

**Peer Replacement:**

Implemented a basic full-bucket replacement mechanism.

- Identified the oldest peer in a full bucket.
- Supported checking peer availability through a ping callback.
- Retained and refreshed an existing peer if it responded.
- Replaced an existing peer when the replacement policy determined it should be removed.

**Closest-Peer Lookup:**

Implemented closest-peer identification using XOR distance.

- Collected peers from all routing buckets.
- Calculated XOR distance between each peer and a target node.
- Sorted peers according to increasing XOR distance.
- Returned the requested number of closest peers.

**Routing Table Statistics:**

Added routing table statistics to monitor the current peer distribution, including:

- Total number of known peers.
- Number of active routing buckets.
- Total number of routing buckets.
- Configured bucket capacity.

**Testing and Verification:**

Created an automated unit testing module using Python's built-in `unittest` framework.

Verified the following functionalities:

- Peer insertion into routing buckets.
- Closest-peer lookup using XOR distance.
- Duplicate peer detection and refresh.
- Prevention of self-node registration.
- Routing table statistics.
- XOR distance calculation and symmetry.

**Test Results:**

- Peer insertion – Passed.
- Closest-peer lookup – Passed.
- Duplicate peer refresh – Passed.
- Self-node prevention – Passed.
- Routing table statistics – Passed.
- XOR distance calculation – Passed.

**Total Tests: 6**

**Passed: 6**

**Failed: 0**

**Result:** Day 9 successfully implemented and tested the Kademlia routing table foundation, establishing structured peer management, K-Bucket organization and XOR-based closest-peer identification.

The routing table provides the foundation for subsequent bootstrap-based peer discovery, dynamic node joining and iterative peer lookup.

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

## Week 2 Overall Achievements So Far

By the end of Day 9, MeshWeaver has established the initial DHT foundation and implemented a structured Kademlia-inspired routing table.

Completed capabilities include:

- 160-bit node identity generation and validation.
- XOR-based logical distance calculation.
- Peer information data structures.
- Peer activity timestamp management.
- Peer information serialization and deserialization.
- 160 K-Bucket routing table organization.
- Configurable bucket capacity.
- Duplicate peer detection and refresh.
- Full-bucket peer replacement support.
- Closest-peer lookup using XOR distance.
- Routing table statistics.
- Automated routing table unit testing.

The next milestones will extend these foundations into bootstrap-based peer discovery, dynamic node joining, iterative peer lookup and periodic resource gossip.

## Upcoming Development – Week 2

The next development phase will focus on improving decentralized peer discovery, routing, and distributed execution.

Planned development areas include:

1. Developing a bootstrap mechanism for new nodes.
2. Enabling dynamic node joining and peer discovery.
3. Implementing iterative peer lookup.
4. Extending resource gossip with asynchronous background tasks.
5. Sharing CPU and RAM utilization reports with neighboring nodes every 5 seconds.
6. Integrating DHT peer information with existing task distribution.
7. Improving peer failure handling and routing reliability.
8. Testing DHT and gossip integration in multi-node environments.

## Documentation

- [Day 1 – UDP Communication](day1_wk1/README.md)
- [Day 2 – TCP Communication](day2_wk1/README.md)
- [Day 3 – Peer Discovery and Task Management](day3_wk1/README.md)
- [Day 4 – Resource Monitoring and Distributed Task Execution](day4_wk1/README.md)
- [Day 5 – Persistence, Security, Peer Gossip and Monitoring](day5_wk1/README.md)
- [Day 6 – Persistent Recovery Verification and Journal Integrity Auditing](day6_wk1/README.md)
- [Day 7 – Function Serialization, Remote Execution and Load-Based Task Distribution](day7_wk1/README.md)
- [Day 8 – DHT Foundation and Peer Information Management](day8_wk2/README.md)
- [Day 9 – Advanced Kademlia Routing Table and Peer Management](day9_wk2/README.md)

## Current Limitations

- Peer discovery currently uses UDP announcements and configured seed ports; a full Kademlia-based DHT is not yet implemented.
- The Day 8 implementation establishes node identity and XOR distance calculation, while Day 9 introduces routing tables and K-Bucket management. Full iterative DHT lookup is still pending.
- Indirectly learned peers remain unconfirmed until direct communication establishes their availability.
- Dynamic node joining and iterative peer lookup are planned for upcoming Week 2 milestones.
- The Day 8 peer information serialization converts objects into JSON-compatible dictionaries, but actual network transmission of those Day 8 peer records is not yet implemented.
- Node identities are randomly generated at startup in the Day 8 implementation; persistent identity storage across application restarts remains to be implemented.
- Peer information is currently maintained as individual records and routing table entries; automatic stale-peer removal and periodic routing table maintenance remain future improvements.
- IP address validation currently checks for a non-empty string in the Day 9 Peer data structure rather than verifying the complete IP address format.
- The last-seen timestamp can be updated manually, but automatic peer health monitoring and stale-peer removal are not yet implemented in the Day 9 routing table module.
- The Day 9 routing table supports a ping callback interface for full-bucket peer replacement, but actual network-level ping integration remains to be implemented.
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

Week 1 established the foundation for distributed task processing, while Week 2 introduced the components required for decentralized node identification and Kademlia-inspired peer organization.

The implementation of 160-bit node identities, XOR distance calculation, peer information management, K-Bucket routing tables and closest-peer lookup provides the groundwork for bootstrap-based node joining and distributed peer discovery.

The next phase will focus on implementing bootstrap mechanisms, iterative peer lookup and strengthening resource gossip to improve peer discovery, network awareness and task distribution.

The long-term goal is to develop a reliable, secure, and scalable peer-to-peer asynchronous task broker without depending on a centralized message broker.
