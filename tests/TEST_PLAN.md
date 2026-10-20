# Person 3 — Testing, Performance & Integration Plan

## Scope

Project 22: Distributed DNS-Like Name Resolution System using UDP sockets, multiple resolution servers, caching, timeouts, server-failure detection, SDN redirection, and lookup-latency measurement.

This plan is based on the project brief and the currently shared files:
- `client.py`
- `server.py`
- `root.py`
- `topology.py`
- `sdncontroller.py`

The code shared so far is an initial implementation. Tests below should be marked **PASS only after they have actually been run** in the target environment.

## Test environment

- Ubuntu VM with Mininet and Open vSwitch installed
- Three Mininet hosts: `h1`, `h2`, `h3`
- Switch: `s1`
- UDP application port: `9053`
- Primary server: `10.0.0.1`
- Client host: expected to be `10.0.0.2` (verify against final topology)
- Secondary server: `10.0.0.3`

Confirm these assumptions against the final topology before running tests.

## Functional test cases

| ID | Test | Procedure | Expected result | Status |
|---|---|---|---|---|
| F01 | Known domain on primary | Query a domain in the primary server's mapping table | Correct configured IP returned | NOT RUN |
| F02 | Known domain on secondary | Query a domain that only exists in the secondary mapping table | Primary forwards request and returns the secondary answer | NOT RUN |
| F03 | Unknown domain | Query a domain absent from both mapping tables | Controlled error / negative response; no indefinite wait | NOT RUN |
| F04 | Cache miss then hit | Query a secondary-resolved domain twice; verify second query uses cache | First request forwards; second uses cached response | NOT RUN |
| F05 | Client timeout | Stop or block the target server, then issue a query | Client exits or reports timeout within configured limit | NOT RUN |
| F06 | Secondary unavailable | Stop the secondary server and query a domain not found on primary | Controlled failure within a bounded time | NOT RUN |
| F07 | Health check | Send health-check message to each server | Each server under monitoring replies within timeout | NOT RUN |
| F08 | Primary failure detection | Stop primary server and observe controller | Controller detects missed health checks | NOT RUN |
| F09 | SDN redirection | With primary unavailable, issue a query after failover rules install | Request reaches secondary and receives a valid answer | NOT RUN |
| F10 | Recovery | Restore primary server and observe behavior | Recovery follows the documented design; no stale/broken rules | NOT RUN |
| F11 | Multiple requests | Send sequential and concurrent client requests | Responses match requests; no cross-request confusion | NOT RUN |
| F12 | Malformed request | Send truncated or invalid datagram | Server handles it safely and remains available | NOT RUN |

## Performance experiments

### P01 — Lookup latency

For each request, record elapsed time with a monotonic clock:

`latency_ms = (response_time - request_time) * 1000`

Record at least 30 successful samples per condition where practical. Report median and p95, not only the mean.

Conditions:
1. Primary mapping hit
2. Secondary forwarding / cache miss
3. Cache hit after a successful forwarded lookup

Keep the queried domain and network conditions consistent across comparisons. Do not compare a failed request with a successful lookup as if they were equivalent.

### P02 — Failover recovery time

Record:
- `t_failure`: when the primary server is stopped or made unreachable
- `t_recovered`: time when a client request first succeeds through the secondary path

`recovery_time_ms = (t_recovered - t_failure) * 1000`

Repeat the experiment at least five times if practical. Report all trials and the median. State exactly how failure was triggered.

### P03 — Reliability under repeated queries

Send a fixed number of requests (for example, 100) and report:
- successful responses
- failed/time-out responses
- success rate
- median and p95 latency

Only run this after the protocol is stable and the server can safely handle the request pattern.

## Integration checklist

- [ ] Confirm request/response format with Person 1.
- [ ] Confirm addresses, ports, and health-check behavior with Person 2.
- [ ] Confirm the final topology starts reliably.
- [ ] Run one known-domain lookup end to end.
- [ ] Run a secondary-server lookup and verify forwarding.
- [ ] Verify cache behavior with observable evidence.
- [ ] Trigger primary failure and verify SDN redirection.
- [ ] Record latency and failover results.
- [ ] Save commands, logs, and results for reproducibility.

## Important issues to resolve before trusting results

1. The current client sends the domain as plain text after a 12-byte header; all components need to agree on this custom message format, or implement real DNS wire format consistently.
2. The secondary server currently needs health-check handling if the controller or tests will monitor it.
3. Forwarding in the primary server currently waits for a secondary response without a visible timeout.
4. The current controller's OpenFlow rules and failover behavior must be verified in the running Mininet/Open vSwitch environment.
5. The current source files do not show latency measurement or an automated test suite yet.

## Results log template

| Date/run | Scenario | Requests | Successes | Failures | Median latency (ms) | p95 latency (ms) | Notes |
|---|---|---:|---:|---:|---:|---:|---|
| — | Primary hit | — | — | — | — | — | Not run |
| — | Secondary/cache miss | — | — | — | — | — | Not run |
| — | Cache hit | — | — | — | — | — | Not run |
| — | Failover | — | — | — | — | — | Not run |
