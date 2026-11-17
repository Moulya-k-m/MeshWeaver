# Day 8 – Week 2: DHT Foundation, Node Identity and Peer Information Management

## Overview

Day 8 focuses on establishing the foundation for implementing a lightweight Kademlia-based Distributed Hash Table (DHT) in MeshWeaver.

It introduces unique node identity generation, node ID validation, XOR-based distance calculation and peer information management.

These components form the foundation for organizing nodes within a decentralized peer-to-peer network and will be used in subsequent implementations of Kademlia routing tables, dynamic node joining and peer discovery.

The implementation also introduces peer information serialization using JSON-compatible dictionaries, allowing peer details to be converted into transferable data and reconstructed at another node.

Day 8 extends MeshWeaver's distributed networking capabilities by establishing the identity and peer management mechanisms required for decentralized node discovery.

## Project Files

| File | Purpose |
|---|---|
| `node_identity.py` | Generates unique 160-bit node IDs, validates node identities and calculates XOR distance |
| `peer_info.py` | Defines the PeerInfo data structure to store peer identity, IP address, port and last-seen timestamp |
| `test_day8.py` | Tests integration between node identity generation, XOR distance calculation and peer information management |
| `test_edge_cases.py` | Tests invalid inputs, XOR distance properties and peer information validation |
| `test_serialization.py` | Tests peer information serialization and deserialization |

## Features Implemented

### 1. Unique Node Identity Generation

Implemented unique 160-bit node identifier generation using Python's `secrets` module.

Each node requires an identifier to distinguish itself from other nodes in the distributed network.

Features include:

- Generates cryptographically strong random node identifiers.
- Uses a 160-bit identifier space compatible with Kademlia's traditional ID size.
- Converts generated identifiers into 40-character hexadecimal strings.
- Supports generating independent identities for different MeshWeaver nodes.

The generated node ID acts as the logical identity of a node within the DHT.

### 2. Node ID Validation

Implemented validation to ensure that node identifiers follow the required 160-bit hexadecimal format.

Features include:

- Checks whether the supplied node ID is a string.
- Verifies that the identifier contains exactly 40 hexadecimal characters.
- Rejects invalid hexadecimal characters.
- Prevents invalid node identities from being used in XOR distance calculations and peer information creation.

This helps maintain consistency in node identity management.

### 3. XOR-Based Distance Calculation

Implemented the XOR distance algorithm used by Kademlia to measure the logical distance between two node identifiers.

The algorithm converts hexadecimal node IDs into integers and applies the XOR operation.

The distance is calculated using:

`Distance = Node_ID_1 XOR Node_ID_2`

Features include:

- Converts hexadecimal node identifiers into integer representations.
- Calculates XOR distance using Python's bitwise XOR operator.
- Validates both node IDs before performing the calculation.
- Rejects invalid identifiers with appropriate ValueError exceptions.
- Supports comparison of node identities within the 160-bit identifier space.

Smaller XOR distances indicate logically closer nodes in the Kademlia identifier space.

This algorithm will later be used for routing table organization and peer lookup.

### 4. Peer Information Management

Implemented a `PeerInfo` data structure using Python's dataclasses.

It stores the essential information associated with a peer in the MeshWeaver network.

Each peer record contains:

- **Node ID:** Unique 160-bit identity of the peer.
- **IP Address:** Network address of the peer.
- **Port:** Communication port associated with the peer.
- **Last Seen:** Timestamp representing the latest recorded peer activity.

Additional features include:

- Validates peer node IDs during object creation.
- Checks that the IP address is a non-empty string.
- Validates port numbers within the range of 1–65535.
- Rejects invalid peer port values.
- Supports updating the last-seen timestamp whenever peer activity is recorded.
- Provides a method to display stored peer information.

This structure will be reused by the routing table implementation in subsequent stages.

### 5. Peer Information Serialization

Implemented peer information serialization to convert PeerInfo objects into JSON-compatible data.

The `to_dict()` method converts a peer object into a dictionary containing its stored information.

Features include:

- Converts peer information into a dictionary.
- Preserves Node ID, IP address, port and last-seen timestamp.
- Supports JSON encoding using Python's built-in JSON library.
- Allows peer information to be reconstructed from received dictionary data.

This provides a foundation for exchanging peer information through MeshWeaver's existing communication mechanisms.

### 6. Peer Information Deserialization

Implemented peer information reconstruction using the `from_dict()` class method.

The method creates a new PeerInfo object using previously serialized peer information.

Features include:

- Reconstructs peer information from a dictionary.
- Restores the original node identifier.
- Restores IP address and port information.
- Preserves the last-seen timestamp.
- Reuses PeerInfo validation during object reconstruction.

This ensures that serialized peer information can be reconstructed without losing its original field values.

## Testing and Results

### Test 1 – Node Identity Generation

Tested the generation of a random 160-bit node identifier.

Verified that:

- A node ID was generated successfully.
- The generated ID contained 40 hexadecimal characters.
- The generated ID passed validation.

Example output:

`Node ID: c5f6e3d9e4f3812cd37a77be48a2bb0cbc4bd1f6`

`ID Length: 40`

`Valid ID: True`

**Result: Node identity generation and validation verified.**

### Test 2 – XOR Distance Calculation

Tested XOR distance calculation using two predefined node identifiers.

Test inputs:

`Node A = 000000000000000000000000000000000000000a`

`Node B = 000000000000000000000000000000000000000c`

Expected calculation:

`10 XOR 12 = 6`

Example output:

`Distance: 6`

**Result: XOR distance calculation verified.**

### Test 3 – Peer Information Management

Tested the creation of a PeerInfo object with a valid node ID, IP address, port and timestamp.

Verified that:

- Peer information was stored successfully.
- The peer details were displayed correctly.
- The last-seen timestamp was updated successfully.

Example output:

`IP Address: 127.0.0.1`

`Port: 9001`

`Updating peer activity...`

`Updated Last Seen: [updated timestamp]`

**Result: Peer information creation and activity timestamp updates verified.**

### Test 4 – Integration Testing

Tested the integration of node identity generation, XOR distance calculation and peer information management.

Verified that:

- Two independent node identities were generated.
- XOR distance was calculated between the generated IDs.
- Peer information was created