# Day 19 – Reliability-Aware Adaptive Scheduling

## Overview

Day 19 introduces a reliability-aware scheduling decision engine for MeshWeaver. It combines historical node performance with current resource availability to rank eligible nodes and recommend the most suitable node for task execution.

## Objectives

- Incorporate historical node reliability into scheduling decisions.
- Consider CPU and RAM availability.
- Evaluate historical task execution performance.
- Exclude unavailable nodes and nodes with stale resource reports.
- Provide transparent explanations for scheduling decisions.
- Handle insufficient or invalid node data safely.

## Implementation

Implemented `ReliabilityAwareScheduler` with four weighted factors:

| Factor | Weight |
|---|---:|
| Historical reliability | 50% |
| CPU availability | 25% |
| RAM availability | 15% |
| Execution performance | 10% |

### Scheduling Score

The scheduler calculates a weighted score:

`Score = (Reliability × 0.50) + (CPU Availability × 0.25) + (RAM Availability × 0.15) + (Performance × 0.10)`

CPU and RAM availability are calculated as 100 minus their respective usage percentages.

Nodes without sufficient reliability history receive a neutral score of 50. Nodes without valid historical execution-time data also receive a neutral performance score of 50.

## Main Features

1. **Reliability-aware ranking:** Considers each node's historical success rate.
2. **Resource-aware selection:** Considers current CPU and RAM usage.
3. **Performance evaluation:** Rewards nodes with lower historical execution times.
4. **Node eligibility checks:** Excludes dead nodes and nodes with stale reports.
5. **Input validation:** Rejects malformed resource values and invalid task counts.
6. **Explainable decisions:** Returns individual score components and a human-readable reason for the selection.

## Files

- `reliability_scheduler.py` – Scheduling and node-ranking implementation.
- `test_reliability_scheduler.py` – Unit tests for scheduling behaviour and edge cases.

## Testing

Run the tests using:

`python -m pytest day19_wk3/test_reliability_scheduler.py -v`

**Result: 13 tests passed.**

Tests cover node ranking, reliability-based selection, dead-node exclusion, stale-report exclusion, insufficient history, invalid resource values, and missing performance information.

## Integration Status

This module currently operates as a scheduling decision engine using node information supplied to it. The `alive` and `report_fresh` flags are provided by the caller.

Direct integration with MeshWeaver's live peer-discovery and scheduling pipeline remains a future step.

## Outcome

Developed a reliability-aware scheduling layer that extends basic load-based selection by considering historical success, resource availability, and execution performance.