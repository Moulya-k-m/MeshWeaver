# Day 2 – TCP Communication and Node Monitoring

## Overview

Day 2 focuses on TCP-based communication between MeshWeaver nodes. It implements structured JSON messaging, message framing, request handling, and basic server monitoring.

## Project Files

| File | Purpose |
|---|---|
| `framing.py` | Handles length-prefixed JSON message framing |
| `tcp_server.py` | Accepts client connections and processes requests |
| `tcp_client.py` | Sends requests and receives server responses |
| `multi_client_test.py` | Tests simultaneous client connections |

## Features Implemented

### 1. TCP Client-Server Communication
Uses Python's `asyncio` TCP streams to establish communication between clients and the server.

### 2. Message Framing
Uses a 4-byte length header to identify the size of each JSON message, allowing the receiver to read complete messages from the TCP stream.

### 3. Request Handling

| Request | Server Response | Purpose |
|---|---|---|
| `HELLO` | `HELLO_ACK` | Greets the client |
| `ADD` | `RESULT` | Adds two numbers |
| `TIME` | `TIME_RESPONSE` | Returns the current UTC time |
| `STATUS` | `STATUS_RESPONSE` | Reports server monitoring information |
| Unknown request | `ERROR` | Reports an unsupported request |

### 4. Server Monitoring

The STATUS response includes:

- Server running status
- Server uptime in seconds
- Total requests handled
- Number of currently connected clients

### 5. Multiple Client Testing

Implemented a separate test script using `asyncio.gather()` to connect two clients concurrently and verify that both receive responses from the same server.

## Testing and Results

### Test 1 – Request Handling

Verified HELLO, ADD, TIME, STATUS and unknown request handling.

The ADD request with values 20 and 22 returned:

`RESULT: 42`

### Test 2 – Multiple Client Connections

Two clients connected to the server simultaneously.

Both received their HELLO acknowledgements and STATUS responses successfully.

### Test 3 – Active Client Monitoring

Observed the active client count:

| Event | Active Clients |
|---|---:|
| Client A connects | 1 |
| Client B connects | 2 |
| Both request STATUS | 2 |
| Client A disconnects | 1 |
| Client B disconnects | 0 |

The server correctly updated the count as clients connected and disconnected.

## How to Run

Run these commands from the project root directory.

**Start the server:**

```bash
python day2_wk1/tcp_server.py
```

**Run the regular client:**

```bash
python day2_wk1/tcp_client.py
```

**Run the multiple-client test:**

```bash
python day2_wk1/multi_client_test.py
```

Keep the server running in a separate terminal while executing either client.

## Technologies Used

- Python
- Asyncio
- TCP sockets
- JSON
- Struct
- Logging
- Datetime and time

## Learning Outcomes

- Understanding TCP client-server communication.
- Implementing length-prefixed message framing.
- Handling multiple asynchronous client connections.
- Tracking server uptime, requests and active connections.
- Testing communication through client-server interactions.
