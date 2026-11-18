
# Day 9 – Week 2: Advanced Kademlia Routing Table and Peer Management

## Overview

Day 9 focuses on implementing an advanced Kademlia-based routing table for MeshWeaver.

It extends the Day 8 DHT foundation by introducing K-Bucket management, XOR-based peer organization, routing table construction and closest-peer lookup.

The implementation organizes known peers according to their XOR distance from the local node, allowing efficient peer identification and decentralized routing.

It also introduces peer metadata management, duplicate peer detection, peer activity tracking and full-bucket replacement mechanisms.

These components establish the routing infrastructure required for subsequent peer discovery, dynamic node joining and decentralized communication.

## Project Files

| File | Purpose |
|---|---|
| `__init__.py` | Initializes the Day 9 Python package |
| `peer.py` | Defines the Peer data structure with node identity, IP address, port and last-seen timestamp |
| `routing_table.py` | Implements XOR distance, K-Buckets, routing table management, closest-peer lookup and peer replacement |
| `test_routing.py` | Performs automated unit testing of routing table functionality |

## Features Implemented

### 1. 160-bit Node Identity Validation

Implemented node identity validation to ensure compatibility with Kademlia's 160-bit identifier space.

Features include:

- Verifies that node IDs are provided as hexadecimal strings.
- Ensures that each node ID contains exactly 40 hexadecimal characters.
- Rejects invalid hexadecimal identifiers.
- Converts validated identifiers into a consistent lowercase format.
- Supports SHA-1-based node ID generation for testing.

This ensures consistency when calculating distances and organizing peers within the routing table.

### 2. XOR-Based Distance Calculation

Implemented XOR distance calculation to determine the logical distance between two peer identities.

The distance is calculated using:

`Distance = Node_ID_1 XOR Node_ID_2`

Features include:

- Converts hexadecimal node IDs into integer representations.
- Performs bitwise XOR operations.
- Validates node IDs before calculating distance.
- Supports distance-based peer comparison.

Smaller XOR distances represent logically closer nodes in the Kademlia identifier space.

### 3. K-Bucket Implementation

Implemented the K-Bucket data structure used by Kademlia to organize known peers.

Each bucket maintains a limited number of peer records.

Features include:

- Configurable bucket capacity.
- Peer insertion and removal.
- Duplicate peer detection.
- Refreshing the position of existing peers.
- Tracking peer activity order.
- Handling full-bucket conditions.

This provides an organized mechanism for maintaining peer information.

### 4. Kademlia Routing Table Management

Implemented a routing table containing 160 K-Buckets corresponding to the 160-bit node identifier space.

Features include:

- Creates 160 routing buckets for each local node.
- Calculates XOR distance between the local node and discovered peers.
- Determines the appropriate bucket using the distance's highest set bit.
- Automatically inserts peers into their corresponding buckets.
- Prevents the local node from being added as its own peer.
- Maintains peer information across multiple buckets.

This allows each node to organize its known peers according to their logical distance.

### 5. Peer Metadata Management

Implemented a reusable Peer data structure using Python dataclasses.

Each peer record contains:

- **Node ID:** Unique 160-bit identity of the peer.
- **IP Address:** Network address of the peer.
- **Port:** Communication port associated with the peer.
- **Last Seen:** Timestamp representing the latest recorded peer activity.

Additional features include:

- Validates peer identity during object creation.
- Validates IP address and port information.
- Updates the last-seen timestamp.
- Provides dictionary-based peer information representation.

This structure allows peer information to be reused across routing and discovery components.

### 6. Duplicate Peer Detection and Refresh

Implemented duplicate peer detection to prevent multiple entries for the same node.

Features include:

- Checks whether a peer already exists in a bucket.
- Prevents duplicate entries.
- Refreshes the peer's activity timestamp.
- Moves refreshed peers to the most-recently-seen position.

This helps maintain an organized peer list based on recent activity.

### 7. Full-Bucket Peer Replacement

Implemented a basic peer replacement mechanism for handling full K-Buckets.

Features include:

- Identifies the oldest peer in a full bucket.
- Supports checking peer availability through a ping callback.
- Retains and refreshes an existing peer if it responds.
- Replaces an unresponsive peer with a newly discovered peer.

This provides a foundation for maintaining reliable peer information.

### 8. Closest-Peer Lookup

Implemented closest-peer identification using XOR distance.

Features include:

- Collects peers from all routing buckets.
- Calculates XOR distance between each peer and a target node.
- Sorts peers according to increasing XOR distance.
- Returns the requested number of closest peers.

This functionality will support efficient peer lookup and routing in subsequent stages.

### 9. Routing Table Statistics

Implemented routing table statistics to monitor peer distribution.

The statistics include:

- Total number of known peers.
- Number of active routing buckets.
- Total number of routing buckets.
- Configured bucket capacity.

This provides visibility into the routing table's current state.

## Testing and Results

### Test 1 – Peer Insertion

Tested adding peer records to the routing table.

Verified that:

- New peers were accepted successfully.
- Peer information was stored in the appropriate buckets.
- Multiple peers could be maintained.

**Result: Peer insertion verified.**

### Test 2 – Closest-Peer Lookup

Tested identifying the closest peers to a target node using XOR distance.

Verified that:

- Peers were collected from routing buckets.
- XOR distances were calculated.
- Peers were sorted according to distance.
- The requested number of closest peers was returned.

**Result: Closest-peer lookup verified.**

### Test 3 – Duplicate Peer Refresh

Tested inserting an already registered peer.

Verified that:

- Duplicate entries were prevented.
- Existing peer information was refreshed.
- The peer was moved to the most-recently-seen position.

**Result: Duplicate peer handling verified.**

### Test 4 – Self-Node Prevention

Tested attempting to add the local node to its own routing table.

Verified that:

- The local node identity was detected.
- Self-registration was rejected.

**Result: Self-node prevention verified.**

### Test 5 – Routing Table Statistics

Tested the statistics functionality after adding peers.

Verified that:

- Total peer count was calculated.
- Active bucket count was determined.
- Total bucket count was reported.
- Bucket capacity was displayed.

**Result: Routing table statistics verified.**

### Test 6 – XOR Distance Calculation

Tested XOR distance calculation using generated 160-bit node identifiers.

Verified that:

- Valid node IDs were accepted.
- XOR distance was calculated successfully.
- Distance calculation was symmetric.

**Result: XOR distance calculation verified.**

## Overall Testing Result

Automated unit testing was performed using Python's built-in `unittest` framework.

Total Tests: 6

Passed: 6

Failed: 0

**Result: All 6 automated unit tests passed successfully.**

## Outcome

Successfully implemented and tested an advanced Kademlia routing table foundation for MeshWeaver.

The implementation establishes structured peer management, XOR-based routing, K-Bucket organization and closest-peer identification.

These capabilities provide the foundation for integrating peer discovery and dynamic node communication in the subsequent development stages.
