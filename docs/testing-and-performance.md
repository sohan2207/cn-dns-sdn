Testing and Performance Report --- DNS-like SDN
Project: Distributed DNS-like Name Resolution System
Testing role: Test automation, performance benchmarking, and
integration verification
Branch: sritej/testing-benchmarks
Latest verified run: 20 October 2026, 21:50:44
Latest report: reports/test_report_20261020_215031.txt
1. Objective
Verify that the custom UDP DNS-like protocol resolves configured
records, supports forwarding from the primary server to the secondary
server, produces repeatable latency measurements, and can redirect
client requests to the secondary server after the primary DNS process
fails.

This is a project-specific DNS-like protocol on UDP port 9053, not a
claim of compatibility with the standard DNS protocol on port 53.
2. Test environment
The recorded run used an Ubuntu VM with Mininet and Open vSwitch. The
programmatic test topology contains three hosts and one switch:

  Node   Address / role
  h1   Primary DNS server --- 10.0.0.1:9053
  h2   Client and controller health-probe namespace --- 10.0.0.2
  h3   Secondary DNS server --- 10.0.0.3:9053
  s1   Open vSwitch switch

The automated runner starts the topology and services, performs protocol
unit tests, DNS smoke tests, benchmarks, and simulated primary failure,
then writes a timestamped report and server/controller logs under
reports/.
3. Latest recorded results
The latest successful run reported 21 passed, 0 failed.

  Test area                                             Recorded result
  Protocol helper unit tests                            7/7 passed
  DNS smoke tests                                       3/3 passed
  example.com benchmark                               30/30 successful
  netflix.com benchmark                               30/30 successful
  Primary health check before failure                   Passed
  Controller detects primary failure                    Passed
  Failover rules installed and visible                  Passed
  Query to primary IP after failure reaches secondary   Passed
  Mininet cleanup                                       Completed cleanly

The report's total count includes the runner's checks and stage
validations; the table above groups the principal outcomes rather than
attempting to reconstruct each individual assertion.
4. Benchmark measurements
Measurements from the latest successful run:

  Domain            Successful requests    Minimum     Median        P95    Maximum
  example.com                   30/30   0.082 ms   0.117 ms   0.264 ms   0.274 ms
  netflix.com                   30/30   0.067 ms   0.084 ms   0.164 ms   0.174 ms

These are measurements from a local Mininet VM and a 30-request sample
per domain. They are not production-scale performance guarantees.
Results can vary with host load, virtualization, and environment.
5. Failover scenario
The runner performed the following sequence:
1. Confirmed the primary DNS server responded before failure.
2. Stopped the primary DNS process to simulate failure.
3. The controller missed two health probes and declared the primary
   unavailable.
4. The controller installed OpenFlow rules on s1.
5. A client query sent to the primary address 10.0.0.1:9053 returned
   the secondary server's configured answer for netflix.com:
   192.27.78.9.
6. The flow dump showed priority-100 UDP rules rewriting the
   destination to 10.0.0.3, the destination MAC to
   00:00:00:00:00:03, and the reply source address to 10.0.0.1.
This verifies the tested failover path for the simulated primary-process
failure in this topology.
6. How to reproduce
From the project root, with the project's dependencies installed:
python3 -m py_compile topology.py server.py sdncontroller.py run_all_tests.py
sudo mn -c
sudo python3 -u run_all_tests.py
Do not start topology.py separately before running the automated
runner, because the runner creates its own topology.

After the run, inspect the newly created reports/test_report_*.txt and
matching test_primary_*.log, test_secondary_*.log, and
test_controller_*.log files.
7. Current coverage and limitations
Verified by the recorded run
- Protocol helper parsing/building unit tests.
- Successful lookup for the three configured test domains.
- Primary-to-secondary forwarding for the tested secondary record.
- 30 successful requests for each of two benchmark domains.
- Controller health detection after the primary process is stopped.
- OpenFlow rule installation and successful query through the primary
  IP after failover.
Recommended additional tests --- not yet evidenced by the recorded run
These should only be marked complete after they are implemented and
executed:
- Malformed or truncated UDP request handling.
- Unknown domain handling when no server has the record.
- Repeated requests using different transaction IDs, including
  cache-hit transaction-ID preservation.
- Secondary server failure while the primary is running.
- Primary recovery behavior and whether failover rules are removed or
  updated.
- Repeated failover runs to check for stale flows and leaked
  processes.
- Benchmark runs with larger sample sizes and under different host
  loads.
The existing passing run does not establish that these untested
scenarios work. Prioritize cases required by the assignment
specification and team agreement.
8. Evidence files
Keep the following latest-run files as evidence:
- reports/test_report_20261020_215031.txt
- reports/test_primary_20261020_215031.log
- reports/test_secondary_20261020_215031.log
- reports/test_controller_20261020_215031.log
Generated reports are excluded from Git via the repository's reports/
ignore rule. Share the report separately if your instructor or team
needs it.
9. Conclusion
In the recorded local run, the automated suite passed with zero
failures. The run verified normal DNS-like resolution, the two-domain
benchmark sample, and the tested SDN failover path. Additional edge
cases listed above remain follow-up coverage rather than completed
results.
