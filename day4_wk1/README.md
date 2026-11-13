
## Day 4 - Resource Monitoring and Task Execution

### Implemented Features

- CPU and RAM resource monitoring using psutil.
- Periodic resource gossip between peer nodes.
- Load-aware task scheduling to select the least-loaded peer.
- Task forwarding between nodes.
- Asynchronous worker execution.
- Task failure handling and automatic retries.
- Exponential retry backoff (1-second and 2-second delays).

### Testing

- Verified resource reports between two nodes.
- Verified task forwarding between nodes.
- Tested arithmetic task execution.
- Tested division-by-zero failure handling.
- Verified two retry attempts with exponential delays.

### Outcome

Successfully implemented and tested resource-aware task distribution and worker execution across multiple peer nodes.
