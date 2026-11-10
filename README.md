# MeshWeaver

**A decentralized asynchronous Python task execution framework for peer-to-peer distributed computing.**

MeshWeaver is an internship project at Infotact exploring decentralized task execution through asynchronous networking and remote Python function execution.

## Week 1 — Networking & Remote Execution

### Objectives
- Establish asynchronous communication between Python nodes.
- Implement TCP-based client-server communication.
- Develop a structured message protocol.
- Serialize Python functions and arguments using `cloudpickle`.
- Execute serialized functions remotely.
- Return execution results to the requesting node.

### Technology Stack
- **Python** — Core implementation
- **asyncio** — Asynchronous networking and task execution
- **TCP / UDP** — Network communication
- **cloudpickle** — Python function serialization

### Project Structure

```text
MeshWeaver/
├── meshweaver/
│   ├── __init__.py
│   ├── node.py
│   ├── protocol.py
│   └── serialization.py
├── tests/
│   ├── test_protocol.py
│   └── test_serialization.py
├── examples/
│   ├── echo_demo.py
│   └── remote_task_demo.py
├── README.md
└── requirements.txt
```

### Development Status

Currently under development.

Week 1 focuses on establishing the communication and execution foundation required for distributed task processing.

## Internship

Developed as part of the **Infotact MeshWeaver Internship Project**.
