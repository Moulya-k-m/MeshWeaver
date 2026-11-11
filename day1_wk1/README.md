# Week 1 – Day 1: UDP Communication and Network Monitoring

## Overview
Implemented asynchronous UDP communication between two nodes using Python. The sender transmits PING messages, and the listener responds with PONG messages.

## Files
- `sender.py` – Sends PING messages and measures network performance.
- `listener.py` – Receives PING messages, validates them and sends PONG responses.

## Features Implemented
- Asynchronous UDP communication using `asyncio`.
- Unique node ID generation.
- JSON-based PING/PONG message exchange.
- Sequence number tracking.
- Invalid packet validation.
- Response timeout handling.
- Round Trip Time (RTT) measurement.
- Jitter calculation using consecutive successful RTT samples.
- Packet loss calculation.
- Network health classification: HEALTHY, UNSTABLE and POOR.
- Listener statistics for received PINGs, invalid packets and sent PONGs.

## Network Health Conditions

The initial classification thresholds are:

- **HEALTHY:** Packet loss is 0%, average RTT is below 100 ms and average jitter is below 20 ms.
- **UNSTABLE:** Packet loss is above 0%, average RTT is at least 100 ms or average jitter is at least 20 ms, unless a POOR condition applies.
- **POOR:** No responses received, packet loss is at least 5%, average RTT is at least 250 ms or average jitter is at least 50 ms.

These are initial project-defined thresholds for testing.

## Test Results

### Test 1: Successful Communication

- Pings sent: 5
- Responses received: 5
- Packet loss: 0%
- Average RTT: 1.67 ms
- Average jitter: 0.70 ms
- Network Health: HEALTHY

### Test 2: Listener Unavailable

- Pings sent: 5
- Responses received: 0
- Packet loss: 100%
- Network Health: POOR
- Sender detected missing responses through timeouts.

## How to Run

Open two terminals from the project root.

**Terminal 1 – Start listener:**

```bash
python day1_wk1/listener.py
```

**Terminal 2 – Start sender:**

```bash
python day1_wk1/sender.py
```

## Technologies Used
Python, asyncio, UDP, JSON, hashlib, uuid and logging.