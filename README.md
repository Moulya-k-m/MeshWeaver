# MeshWeaver – Week 1 Progress Report

**Project:** MeshWeaver – Zero-Dependency P2P Async Task Broker  
**Organization:** INFOTACT Solutions  
**Domain:** Distributed Systems & Edge Computing  
**Week:** 1 (9 Nov – 16 Nov 2026)

---

## 1. Project Overview

Task queues such as Celery depend on a central broker (Redis or RabbitMQ). On edge deployments with hundreds of devices, such as Raspberry Pis in a factory or field, that broker becomes a single point of failure and is hard to configure on every device.

MeshWeaver is a decentralized task queue written in pure Python with **no central server**. Nodes talk directly to each other over `asyncio` UDP/TCP and form a peer-to-peer mesh. The planned features are:

- Node discovery using a Kademlia DHT, with no hardcoded IPs
- Gossip of CPU/RAM load between neighbors every 5 seconds
- Python functions sent between nodes using `cloudpickle`
- Task routing to the least-loaded node
- Automatic task re-queue when a node fails

---

## 2. Week 1 Goal

Build the foundation: two Python nodes that communicate over `asyncio` UDP, and then send a serialized Python function over a socket and execute it on the receiving node.

---

## 3. Day 1 – 10 November 2026 (Completed)

### Work Completed

- Installed and set up Python, VS Code, and Git.
- Created a Python virtual environment and the project structure.
- Explored UDP communication using Python sockets and `asyncio`.
- Implemented a UDP listener node and a UDP sender node.
- Established communication between two local Python instances using PING and PONG messages.
- Designed a JSON message format with a message type, sequence number, and a random 160-bit node ID (the same ID size used by Kademlia).
- Matched each reply to its request using sequence numbers, since UDP can drop, duplicate, or reorder packets.
- Added input validation so a malformed packet is logged and dropped without crashing the node.
- Added timeout handling and structured logging.
- Added command-line options (`--host`, `--port`, `--count`, `--timeout`) so multiple nodes can run on different ports.
- Committed the work to Git.

### Files Created

- `day1/listener.py`: UDP node that replies PONG to every valid PING
- `day1/sender.py`: UDP node that sends pings and reports round-trip time and packet loss
- `README.md`, `requirements.txt`, `.gitignore`

### Test Results

| Test | Result |
|---|---|
| Pings sent / received | 5 / 5 |
| Packet loss | 0% |
| Round-trip time (min / avg / max) | 0.81 ms / 1.28 ms / 2.09 ms |
| Malformed packet sent to listener | Warning logged, listener kept running |
| Listener stopped, sender run | Timeouts reported (UDP gives no error, so timeouts are required) |

### Key Learnings

- UDP is fast and connectionless, but does not guarantee delivery. Every network call needs a timeout.
- A node must never crash because of bad input from a peer.
- A request/reply pattern using a `sequence number -> Future` map will be reused for DHT lookups and task acknowledgements.
- `time.sleep()` blocks the whole node. Use `await asyncio.sleep()` inside async code.

---

## 4. Revised Plan (Day 2 – Day 6)

The original Day 2 ("further UDP testing") has been replaced. Sending a function between nodes needs a reliable connection, so the plan now moves to TCP and serialization, which is what the Week 1 requirements ask for.

| Day | Date | Planned Activity | Expected Output |
|---|---|---|---|
| Day 2 | 11 Nov | Learn TCP sockets with `asyncio`; build a TCP server and client | Two nodes exchange messages over TCP |
| Day 3 | 12 Nov | Serialize a Python function and its arguments with `cloudpickle` | Function packed into bytes and restored in a test script |
| Day 4 | 13 Nov | Send the serialized function from one node to another over TCP | Receiver gets the full function bytes intact |
| Day 5 | 14 Nov | Execute the received function on the receiver and return the result | Sender receives the computed result |
| Day 6 | 15 Nov | Test and integrate Week 1 components; add message signing (HMAC) before unpickling | Working end-to-end demo; unsigned messages rejected |
| Buffer | 16 Nov | Fix issues, clean up code, update documentation, final commit | Week 1 submission ready |

---

## 5. Security Note

`cloudpickle` (like `pickle`) runs code when it loads data. A node that unpickles bytes from an untrusted peer can be fully compromised. The plan is to sign every message (HMAC with a shared secret) and **verify the signature before unpickling**. Messages that fail verification are rejected. This is scheduled for Day 6.

---

## 6. Current Status

| Item | Status |
|---|---|
| Development environment | Done |
| UDP listener and sender | Done |
| Message validation, timeouts, logging | Done |
| TCP communication | Not started |
| Task serialization (`cloudpickle`) | Not started |
| Remote function execution | Not started |

**Completed:** Asynchronous UDP communication between two local nodes, tested and committed.

**Next Step (Day 2):** Build a TCP server and client with `asyncio`, as the base for sending serialized tasks.