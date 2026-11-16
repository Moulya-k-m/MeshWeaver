# Day 7 – Function Serialization, Remote Execution and Load-Based Task Distribution

## Overview

Day 7 focuses on enabling MeshWeaver to execute Python functions across multiple distributed nodes.

It introduces function serialization and deserialization using Cloudpickle, remote function execution through the existing task-processing system, and load-based task forwarding between connected peers.

These enhancements allow a node to submit a Python function for execution, transfer the serialized function package to another node, and execute it remotely without requiring the function to be manually implemented on the receiving node.

Day 7 extends MeshWeaver from basic task communication and scheduling into distributed function execution.

## Project Files

| File | Purpose |
|---|---|
| `serializer.py` | Serializes and deserializes Python functions, arguments and keyword arguments using Cloudpickle |
| `test_serialization.py` | Tests function serialization, reconstruction and execution |
| `test_worker.py` | Verifies that the worker can execute serialized Python functions |
| `test_remote_execution.py` | Tests remote function submission and result retrieval through a MeshWeaver node |
| `test_load_balance.py` | Tests task forwarding between two nodes under load |
| `day5_wk1/worker.py` | Integrates remote function execution into the existing worker |
| `day5_wk1/node.py` | Handles task submission, peer selection, forwarding and remote result communication |
| `day5_wk1/security.py` | Provides authenticated communication for remote requests and responses |

## Features Implemented

### 1. Python Function Serialization Using Cloudpickle

Implemented function serialization using the Cloudpickle library.

Serialization converts a Python function and its arguments into a transferable representation that can be sent between distributed nodes.

Features include:

- Serializes Python functions.
- Supports positional arguments and keyword arguments.
- Converts serialized binary data into Base64-encoded text.
- Validates function call inputs before serialization.
- Enforces a maximum serialized payload size of 700 KB.
- Handles invalid Base64 data and oversized payloads.

This allows Python function packages to be transferred through MeshWeaver's existing JSON-based TCP communication.

### 2. Function Deserialization and Reconstruction

Implemented deserialization to reconstruct the original function package at the receiving node.

Features include:

- Decodes Base64-encoded serialized data.
- Reconstructs Python functions using Cloudpickle.
- Extracts the original function and its arguments.
- Validates the reconstructed function.
- Checks that positional arguments and keyword arguments have valid types.
- Rejects invalid function packages.

The reconstructed function can then be executed by the receiving worker.

### 3. Remote Function Execution

Integrated remote function execution into the existing worker.

A new `REMOTE_CALL` operation was introduced to allow workers to execute serialized Python functions.

Features include:

- Accepts serialized function packages.
- Deserializes the received function.
- Executes the reconstructed function with its original arguments.
- Returns the execution result.
- Integrates with the existing task-processing mechanism.

This enables MeshWeaver nodes to execute functions received from other nodes rather than being restricted to locally defined task operations.

### 4. Integration with the Existing Task Queue

Connected remote function execution with the existing task submission and processing system.

Features include:

- Accepts remote function execution requests.
- Creates task entries in the task store.
- Adds accepted tasks to the processing queue.
- Allows workers to pick up and execute remote function tasks.
- Stores task execution results.
- Supports result retrieval using the task ID.

This connects function serialization with MeshWeaver's existing task management architecture.

### 5. Load-Based Task Distribution

Enhanced task scheduling to consider the resource load of connected peers.

The node compares its local load score with the load score reported by another peer.

When a suitable peer has a lower load score, the task can be forwarded to that peer for execution.

Features include:

- Retrieves local node load information.
- Uses resource information received through peer gossip.
- Compares local and peer load scores.
- Selects a less-loaded peer for task forwarding.
- Forwards tasks through authenticated TCP communication.
- Maintains task identification during forwarding.
- Handles successful and unsuccessful forwarding attempts.

This helps distribute tasks across available nodes instead of executing every task locally.

### 6. Authenticated Remote Task Forwarding

Integrated the existing HMAC-SHA256 authentication mechanism into remote task communication.

Features include:

- Signs outgoing task requests.
- Verifies incoming requests.
- Signs responses before transmission.
- Verifies responses received from remote nodes.
- Re-signs forwarded responses using the receiving node's authentication mechanism.
- Rejects responses with invalid signatures.

This ensures that remote task communication continues to use the authentication mechanism introduced in the earlier implementation.

### 7. Remote Task Result Retrieval

Integrated task result retrieval with remote task forwarding.

When a task is forwarded to another node, the submitting node maintains information about the remote task location.

This allows the submitting node to identify the peer responsible for executing the task.

Features include:

- Maintains remote task identification.
- Tracks the peer to which a task was forwarded.
- Uses the task ID to request execution status.
- Supports retrieving results from the remote node through the submitting node.

The end-to-end result retrieval path is included in the remote execution test.

## Testing and Results

### Test 1 – Function Serialization

Tested the serialization of a Python multiplication function using Cloudpickle.

The function was:

`multiply(10, 20)`

Verified that the function could be serialized and converted into Base64-encoded data.

**Result: Function serialization verified.**

### Test 2 – Function Deserialization

Tested the reconstruction of the serialized function package.

Verified that:

- The encoded data was successfully decoded.
- The original function was reconstructed.
- Positional arguments were restored.
- The reconstructed function could be executed.

Example output:

`Serialization successful!`

`Deserialization successful!`

`Execution result: 200`

**Result: Function reconstruction and execution verified.**

### Test 3 – Worker Integration

Tested the integration of the `REMOTE_CALL` operation with the existing worker.

Submitted a serialized multiplication function to the worker.

Verified that the worker successfully reconstructed and executed the function.

Example output:

`Worker execution result: 200`

`WORKER TEST PASSED!`

**Result: Remote function execution through the worker verified.**

### Test 4 – Remote Function Execution Through a Node

Started a MeshWeaver node and submitted a serialized Python function through TCP communication.

The submitted function was:

`multiply(10, 20)`

Verified that:

- The task was accepted by the node.
- The task was assigned a task ID.
- The worker executed the function.
- The execution result was stored.
- The result was retrieved through the task result mechanism.

Example output:

`Task accepted!`

`Task completed!`

`Result: {'ok': True, 'value': 200}`

`REMOTE EXECUTION TEST PASSED!`

**Result: Remote function submission and execution verified.**

### Test 5 – Two-Node Load-Based Task Forwarding

Tested task distribution using two independent MeshWeaver nodes.

Node configuration:

| Node | TCP Port | UDP Port |
|---|---:|---:|
| Node 1 | 8001 | 50001 |
| Node 2 | 8002 | 50002 |

Both nodes were started with the same configured shared secret.

Verified that:

- Both nodes successfully discovered each other.
- Resource information was exchanged through gossip.
- Local and peer load scores were compared.
- Node 1 identified Node 2 as the less-loaded peer.
- Submitted tasks were forwarded to Node 2.

Observed log messages:

`LOCAL LOAD SCORE: 36.59`

`PEER LOAD SCORE: 32.95`

`Attempting to forward task to peer`

`Task successfully forwarded to peer`

**Result: Load-based task forwarding verified.**

### Test 6 – Distributed Task Execution

Submitted eight tasks through Node 1 while Node 2 was available as a remote execution peer.

Verified through the Node 2 terminal that all eight forwarded tasks were:

- Successfully received.
- Accepted by the receiving node.
- Picked up by the worker.
- Executed successfully.
- Marked as completed.

Example execution logs:

`Accepted forwarded task from node ba1ced68`

`Picked up task`

`Task completed: Load test 0`

The same successful execution pattern was observed for all eight submitted tasks.

**Result: Eight out of eight forwarded tasks successfully executed on Node 2.**

## How to Run

Run the following commands from the MeshWeaver project directory.

### 1. Activate the Virtual Environment

```powershell
.\.venv\Scripts\Activate.ps1
```

### 2. Configure the Shared Secret

Set the same environment variable in every terminal used to start the nodes:

```powershell
$env:MESHWEAVER_SECRET = "MeshWeaver_Day7_Test_Secret_2026"
```

### 3. Start Node 1

Open the first terminal and navigate to `day7_wk1`:

```powershell
cd day7_wk1
python ..\day5_wk1\node.py --tcp 8001
```

### 4. Start Node 2

Open a second terminal:

```powershell
cd day7_wk1
$env:MESHWEAVER_SECRET = "MeshWeaver_Day7_Test_Secret_2026"
python ..\day5_wk1\node.py --tcp 8002
```

Keep both nodes running to allow peer discovery, resource gossip and task forwarding.

### 5. Test Function Serialization

Open another terminal:

```powershell
cd day7_wk1
python test_serialization.py
```

### 6. Test Worker Execution

```powershell
python test_worker.py
```

### 7. Test Remote Function Execution

```powershell
python test_remote_execution.py
```

### 8. Test Load-Based Task Forwarding

```powershell
python test_load_balance.py
```

Observe Node 1 and Node 2 terminals to verify that tasks are forwarded and executed remotely.

## Known Limitations

- Cloudpickle supports Python function serialization, but deserializing untrusted serialized data can execute arbitrary code. Remote deserialization must therefore be restricted to trusted and authenticated peers; HMAC authentication does not provide a code-execution sandbox.
- The maximum serialized function package size is currently limited to 700 KB.
- The current implementation uses a shared secret for message authentication.
- Load-based scheduling depends on the availability and freshness of peer resource reports.
- The current load distribution test demonstrates forwarding between two local nodes; large-scale cluster testing remains pending.
- The current test demonstrates eight successful forwarded task executions. Exhaustive testing of remote result retrieval for all forwarded tasks is a separate validation step.
- Advanced fault tolerance, automatic reassignment of failed remote tasks and exactly-once execution are not guaranteed.
- More advanced distributed discovery using a Kademlia-based DHT remains a future enhancement.

## Technologies Used

- Python
- Asyncio
- TCP and UDP sockets
- Cloudpickle
- Base64
- JSON
- HMAC-SHA256
- Hashlib
- HMAC
- UUID
- Task queues
- Distributed scheduling
- Resource monitoring
- Peer-to-peer communication

## Conclusion

Day 7 extends MeshWeaver with Python function serialization, remote execution and load-based task distribution.

The implementation enables connected nodes to exchange serialized Python functions, reconstruct and execute them remotely, and distribute tasks based on peer resource availability.

Testing demonstrated successful function serialization, worker integration, remote execution and task forwarding between two independent nodes.

The successful execution of eight forwarded tasks demonstrates the progress made toward building a decentralized asynchronous task broker capable of distributing computational work across multiple peers.