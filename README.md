## Daily Development Progress

### Day 1 – Project Setup & Basic UDP Communication

**Date:** 9 November 2026

**Tasks Completed:**
- Set up the Python virtual environment.
- Created the MeshWeaver project folder structure.
- Configured `.gitignore` and `requirements.txt`.
- Studied UDP socket programming.
- Implemented a UDP receiver (Node B).
- Implemented a UDP sender (Node A).
- Established communication between Node A and Node B using UDP.
- Implemented and tested the ACK response mechanism.
- Resolved a UDP port conflict.

**Files Created:**
- `examples/sender.py`
- `examples/receiver.py`

**Test Result:** Successfully sent a message from Node A to Node B and received an acknowledgement response.

**Status:** COMPLETED

---

### Day 2 – Asynchronous UDP Communication

**Date:** 10 November 2026

**Tasks Completed:**
- Studied asynchronous programming and Python `asyncio`.
- Learned about event loops and asynchronous execution.
- Implemented an asynchronous UDP receiver using `asyncio.DatagramProtocol`.
- Implemented an asynchronous UDP sender.
- Established asynchronous communication using `create_datagram_endpoint()`.
- Implemented message transmission and ACK response handling.
- Added timeout handling using `asyncio.wait_for()`.
- Successfully tested asynchronous message transmission and ACK response.

**Files Created:**
- `examples/async_sender.py`
- `examples/async_receiver.py`

**Test Result:** Successfully sent an asynchronous UDP message from Node A to Node B and received the acknowledgement response.

**Status:** COMPLETED

---

### Day 3 – Function Serialization Using cloudpickle

**Date:** 11 November 2026

**Tasks Completed:**
- Studied Python function serialization and deserialization.
- Used `cloudpickle` to serialize a Python function.
- Converted the function into serialized byte data using `cloudpickle.dumps()`.
- Restored the function using `cloudpickle.loads()`.
- Executed the restored function successfully.
- Verified the calculated result.

**Files Created:**
- `examples/serialization_demo.py`

**Test Result:**
- Function serialized successfully.
- Serialized data size: 563 bytes.
- Function deserialized successfully.
- Execution result: 1000.

**Status:** COMPLETED

---

### Day 4 – Serialized Function Transfer

**Date:** 12 November 2026

**Planned Tasks:**
- Transfer serialized function data between two nodes.
- Receive serialized data on the receiving node.
- Deserialize the function on Node B.
- Verify successful function transfer.

**Status:** PENDING

---

### Day 5 – Basic Remote Function Execution

**Date:** 13 November 2026

**Planned Tasks:**
- Execute the received function on the remote node.
- Capture the execution result.
- Send the result back to the sender.
- Test the complete remote execution workflow.

**Status:** PENDING

---

## Week 1 Summary

**Completed:**
- Day 1: Project setup and basic UDP communication.
- Day 2: Asynchronous UDP communication using Python `asyncio`.
- Day 3: Function serialization and deserialization using `cloudpickle`.

**Upcoming:**
- Day 4: Transfer serialized functions between nodes.
- Day 5: Execute remote functions and return results.

**Current Milestone:** Successfully implemented and tested synchronous UDP communication, asynchronous UDP communication, and local function serialization/deserialization.

**Next Milestone:** Transfer a serialized Python function from Node A to Node B and prepare for remote execution.