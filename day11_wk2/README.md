
# Day 11 – Kademlia FIND_NODE and Iterative Lookup

## Objective
Implemented peer discovery using the Kademlia FIND_NODE protocol and iterative node lookup.

## Features
- TCP-based FIND_NODE client and server.
- JSON request and response handling.
- Node ID validation.
- Retrieval of the 20 closest known peers.
- XOR distance-based peer ranking.
- Iterative lookup using parallel peer queries.
- Alpha parameter for controlling concurrent requests.
- Discovery and storage of new peers during lookup.
- Exclusion of the local node from discovered peers.
- Handling of invalid IDs, connection failures and timeouts.

## Files
- find_node.py – FIND_NODE client and server.
- test_find_node.py – FIND_NODE protocol tests.
- lookup_manager.py – Iterative lookup implementation.
- test_lookup_manager.py – Iterative lookup tests.

## Testing
Run Day 11 tests:

```bash
python -m unittest day11_wk2.test_find_node day11_wk2.test_lookup_manager -v
```

Run all project tests:

```bash
python -m unittest discover -v
```

## Test Results
- FIND_NODE tests: 4 passed.
- Iterative lookup tests: 5 passed.
- Day 9, Day 10 and Day 11 combined: 19 passed.

## Status
Day 11 implementation and tests completed successfully.
