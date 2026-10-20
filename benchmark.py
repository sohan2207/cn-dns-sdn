"""Measure round-trip latency for the current DNS-like UDP protocol.

Run from Mininet host h2 after starting the primary and secondary servers:
    python3 benchmark.py --domain netflix.com --count 30

This script reports measurements; it does not prove a cache hit by itself.
The current server has no cache-hit telemetry, so compare the first lookup with
later lookups as an indicative experiment and document that limitation.
"""

import argparse
import statistics
import sys

from tests.protocol_helpers import query_once


def percentile(values, pct):
    ordered = sorted(values)
    if not ordered:
        return float("nan")
    index = round((pct / 100) * (len(ordered) - 1))
    return ordered[index]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--host", default="10.0.0.1", help="Primary server IP (default: 10.0.0.1)")
    parser.add_argument("--port", type=int, default=9053, help="UDP port (default: 9053)")
    parser.add_argument("--domain", default="netflix.com", help="Domain to query (default: netflix.com)")
    parser.add_argument("--count", type=int, default=30, help="Number of requests (minimum 2)")
    parser.add_argument("--timeout", type=float, default=2.0, help="Per-request timeout in seconds")
    args = parser.parse_args()

    if args.count < 2:
        parser.error("--count must be at least 2")

    latencies = []
    successes = 0
    failures = 0
    print(f"Target: {args.host}:{args.port} | domain={args.domain} | requests={args.count}")

    for i in range(args.count):
        txid = (50000 + i) % 65536
        try:
            response = query_once(args.host, args.port, args.domain, args.timeout, txid)
            latencies.append(response.latency_ms)
            successes += 1
            print(f"{i + 1:02d}. answer={response.answer!r} latency={response.latency_ms:.3f} ms")
        except Exception as exc:
            failures += 1
            print(f"{i + 1:02d}. FAILED: {type(exc).__name__}: {exc}", file=sys.stderr)

    print("\n=== Summary ===")
    print(f"Successful requests: {successes}/{args.count}")
    print(f"Failed requests:     {failures}/{args.count}")
    if latencies:
        print(f"Minimum latency:     {min(latencies):.3f} ms")
        print(f"Median latency:      {statistics.median(latencies):.3f} ms")
        print(f"p95 latency:         {percentile(latencies, 95):.3f} ms")
        print(f"Maximum latency:     {max(latencies):.3f} ms")
        print(f"First request:       {latencies[0]:.3f} ms")
        if len(latencies) > 1:
            print(f"Later requests avg:  {statistics.mean(latencies[1:]):.3f} ms")
    if failures:
        sys.exit(1)


if __name__ == "__main__":
    main()
