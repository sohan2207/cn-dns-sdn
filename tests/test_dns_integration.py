"""Opt-in integration tests for the running Mininet DNS-like service.

Run inside the Mininet client host after starting both DNS servers:
    RUN_DNS_INTEGRATION=1 python3 -m unittest discover -s tests -p 'test_dns_integration.py' -v

The tests use the starter code's custom UDP format, not standard DNS packets.
"""

import os
import unittest

from protocol_helpers import query_once

RUN_INTEGRATION = os.getenv("RUN_DNS_INTEGRATION") == "1"
SERVER_HOST = os.getenv("DNS_SERVER_HOST", "10.0.0.1")
SERVER_PORT = int(os.getenv("DNS_SERVER_PORT", "9053"))
TIMEOUT_S = float(os.getenv("DNS_TIMEOUT_S", "2.0"))


@unittest.skipUnless(RUN_INTEGRATION, "set RUN_DNS_INTEGRATION=1 to run against a live Mininet network")
class DNSIntegrationTests(unittest.TestCase):
    def test_primary_known_domain(self):
        response = query_once(SERVER_HOST, SERVER_PORT, "example.com", TIMEOUT_S, 41001)
        self.assertEqual(response.answer, "93.184.216.34")
        self.assertEqual(response.answer_count, 1)

    def test_another_primary_known_domain(self):
        response = query_once(SERVER_HOST, SERVER_PORT, "google.com", TIMEOUT_S, 41002)
        self.assertEqual(response.answer, "142.250.190.46")
        self.assertEqual(response.answer_count, 1)

    def test_secondary_domain_forwarding(self):
        # netflix.com exists only in the secondary server's mapping in the supplied code.
        response = query_once(SERVER_HOST, SERVER_PORT, "netflix.com", TIMEOUT_S, 41003)
        self.assertEqual(response.answer, "192.27.78.9")
        self.assertEqual(response.answer_count, 1)


if __name__ == "__main__":
    unittest.main()
