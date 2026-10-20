# Team workflow

1. Pull the latest `main` before starting work.
2. Create a branch for each task (for example, `person1/dns-protocol`, `person2/sdn-failover`, `person3/tests-benchmarks`).
3. Keep commits focused and describe what changed.
4. Agree on shared protocol, host addresses, ports, and health-check behavior before changing interfaces.
5. Run the relevant tests and document commands/results in the pull request or commit description.
6. Do not report a test as passing unless it has actually been run.
