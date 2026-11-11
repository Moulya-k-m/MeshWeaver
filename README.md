# MeshWeaver

## Project Overview

MeshWeaver is a Python-based peer-to-peer asynchronous task broker designed to allow multiple nodes to communicate, exchange system information, and distribute tasks efficiently.

The project explores asynchronous networking, node communication, task serialization, resource monitoring, and distributed task execution.

## Project Objectives

- Establish communication between peer nodes.
- Monitor network and node health.
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
| Day 3 | Task serialization and deserialization | Planned |
| Day 4 | Task transfer between nodes | Planned |
| Day 5 | Task execution and result transfer | Planned |
| Day 6 | Integration, authentication using HMAC and reliability improvements | Planned |
| 16 November | Testing, documentation and buffer | Planned |

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
├── .gitignore
├── README.md
└── requirements.txt
```

## Current Progress

### Day 1 – UDP Communication
Implemented asynchronous UDP sender and listener communication using PING/PONG messages. Added RTT, jitter, packet-loss measurement and basic network-health classification.

### Day 2 – TCP Communication
Implemented TCP client-server communication with length-prefixed JSON framing. Added HELLO, ADD, TIME and STATUS requests, server uptime and request monitoring, active-client tracking, and concurrent client testing.

## Upcoming Development

The next development stages focus on:

1. Serializing tasks for transfer between nodes.
2. Transferring task data through TCP.
3. Executing received tasks and returning results.
4. Integrating the communication components.
5. Improving authentication and failure handling.

## Documentation

- [Day 1 – UDP Communication](day1_wk1/README.md)
- [Day 2 – TCP Communication](day2_wk1/README.md)

## Project Status

Week 1 development is in progress. Features listed as planned are not yet implemented.
