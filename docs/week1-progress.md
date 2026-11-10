# MeshWeaver – Week 1 Progress Report

**Project:** MeshWeaver – Zero-Dependency P2P Async Task Broker
**Domain:** Distributed Systems & Edge Computing
**Developer:** Ameesha
**Week:** 1 (7 November – 14 November 2026)

## Week 1 Objective

To establish basic peer-to-peer communication between two nodes using Python UDP sockets and prepare the foundation for asynchronous task execution.

## Day 1 – Project Setup and Basic UDP Communication

**Date:** 10 November 2026

### Tasks Completed
- Configured Python virtual environment.
- Created project folder structure.
- Created `src`, `tests`, `docs`, and `examples` directories.
- Configured `.gitignore` and `requirements.txt`.
- Studied UDP and Python socket programming.
- Implemented UDP sender (Node A).
- Implemented UDP receiver (Node B).
- Established communication using localhost and UDP port 5002.
- Implemented application-level acknowledgement (ACK).
- Tested message transmission and response successfully.
- Identified and resolved a port conflict (WinError 10048).

### Files Created
- `examples/sender.py`
- `examples/receiver.py`

### Test Result

| Test | Result |
|---|---|
| Start UDP receiver | Passed |
| Send message from Node A | Passed |
| Receive message at Node B | Passed |
| Send ACK from Node B | Passed |
| Receive ACK at Node A | Passed |

**Day 1 Status: COMPLETED**

## Week 1 Planned Activities

| Day | Planned Activity | Status |
|---|---|---|
| Day 1 | Project setup and basic UDP communication | Completed |
| Day 2 | Asynchronous UDP communication using asyncio | Pending |
| Day 3 | Function serialization using cloudpickle | Pending |
| Day 4 | Transfer serialized functions between nodes | Pending |
| Day 5 | Execute remote functions and return results | Pending |

## Week 1 Expected Deliverables

1. Working UDP sender and receiver.
2. Asynchronous UDP communication.
3. Function serialization and deserialization.
4. Remote function transmission.
5. Basic remote task execution and result response.

## Current Progress

Successfully established basic UDP communication between two nodes running on the same machine.

**Next Step:** Implement asynchronous UDP communication using Python asyncio.

*Note: Planned activities will be marked completed only after implementation and successful testing.*