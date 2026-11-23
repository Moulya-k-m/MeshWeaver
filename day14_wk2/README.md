# Day 14 – Cluster Integration and Failure Recovery

## Overview
Day 14 focuses on integrating peer discovery with resource gossip and validating communication between multiple MeshWeaver nodes.

The implementation verifies that nodes can discover one another, exchange signed resource reports, update scheduler load information, and clean up resource data when a peer becomes unavailable.

## Features Implemented

### 1. Peer Discovery Integration
- Retrieves peers through the discovery component.
- Registers discovered peers in the peer table.
- Avoids registering the bootstrap server as a regular gossip peer.
- Supports refreshing the