# Distributed DNS-Like Name Resolution System

**Course project:** Computer Networks (CN)  
**Project number:** 22  
**Transport:** UDP sockets  
**Network environment:** Mininet / Open vSwitch / SDN

## Overview

This project implements a simplified DNS-like name-resolution service over UDP. The intended system uses name-to-IP mappings, multiple resolution servers, caching, timeouts, server-failure detection, SDN-controlled redirection, and lookup-latency measurement.

The project requirements and grading guidance are retained in [`docs/SDN-Socket Programming-Guidelines_Rubrics.pdf`](docs/SDN-Socket%20Programming-Guidelines_Rubrics.pdf), and the list of project options is retained in [`docs/SDN_Socket_Programming_30_Projects.xlsx`](docs/SDN_Socket_Programming_30_Projects.xlsx). The Ubuntu Mininet installation guide is in `docs/` as well.

## Current source files

| File | Current intended role |
|---|---|
| `client.py` | Sends a UDP name-resolution request and waits for a response |
| `server.py` | Primary name-resolution server; contains mappings, a cache, and forwarding to the secondary server |
| `root.py` | Secondary name-resolution server with a separate set of mappings |
| `topology.py` | Creates a Mininet topology with three hosts and one switch |
| `sdncontroller.py` | Checks primary-server health and attempts to install OpenFlow rules for redirection |
| `tests/TEST_PLAN.md` | Person 3's functional, integration, and performance test plan |

These descriptions reflect the files' intended roles. They do **not** imply that every feature is complete or verified.

## Current status

The checked-in Python files are the initial source files shared by the team. The end-to-end system has not yet been verified from this repository snapshot. In particular, confirm the message format across the client and servers, health-check behavior, forwarding timeouts, Mininet/Open vSwitch configuration, and actual failover before treating those features as complete.

## Requirements / environment

- Ubuntu environment recommended for the supplied Mininet installation guide
- Python 3
- Mininet
- Open vSwitch utilities (`ovs-ofctl`)

The core Python files use the standard library, but `topology.py` requires Mininet and failover behavior requires a correctly configured Open vSwitch environment. No dependency versions have been pinned yet.

## Running / testing

The exact run commands depend on the final agreed protocol, host addresses, and Mininet setup. Before running the full system:

1. Review the project documents in `docs/`.
2. Agree on addresses, UDP ports, packet format, and health-check messages across all components.
3. Start the Mininet topology and verify host-to-host connectivity.
4. Start the primary and secondary servers, then run a client lookup.
5. Test caching, timeouts, primary failure, and SDN redirection.
6. Record measured results in the Person 3 test plan; mark tests as passed only after observing the result.

See [`tests/TEST_PLAN.md`](tests/TEST_PLAN.md) for the test matrix and performance experiments.

## Team work split

- **Person 1 — DNS resolution and protocol:** `client.py`, `server.py`, `root.py`
- **Person 2 — Mininet and SDN failover:** `topology.py`, `sdncontroller.py`
- **Person 3 — Testing, performance and integration:** `tests/TEST_PLAN.md`, test scripts, benchmarking, integration checks, and documentation

Coordinate interface changes before merging work. Avoid overwriting another member's changes without discussing them first.

## Repository layout

```text
.
├── client.py
├── root.py
├── sdncontroller.py
├── server.py
├── topology.py
├── docs/
│   ├── Mininet Installation Guide on UBUNTU.docx.pdf
│   ├── SDN-Socket Programming-Guidelines_Rubrics.pdf
│   └── SDN_Socket_Programming_30_Projects.xlsx
├── tests/
│   └── TEST_PLAN.md
├── .gitignore
└── README.md
```
