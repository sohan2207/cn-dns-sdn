"""Offline unit tests for Person 3's test helpers; no Mininet needed."""

import struct
import unittest

from protocol_helpers import HEADER_FORMAT, HEADER_SIZE, build_query, parse_response


class ProtocolHelperTests(unittest.TestCase):
    def test_build_query_has_header_and_domain(self):
        packet = build_query("example.com", transaction_id=42)
        self.assertEqual(len(packet[:HEADER_SIZE]), HEADER_SIZE)
        self.assertEqual(packet[HEADER_SIZE:], b"example.com")
        fields = struct.unpack(HEADER_FORMAT, packet[:HEADER_SIZE])
        self.assertEqual(fields[0], 42)
        self.assertEqual(fields[1], 0x0100)
        self.assertEqual(fields[2], 1)

    def test_build_query_strips_whitespace(self):
        self.assertTrue(build_query("  example.com  ").endswith(b"example.com"))

    def test_build_query_rejects_empty_domain(self):
        with self.assertRaises(ValueError):
            build_query("  ")

    def test_build_query_rejects_invalid_transaction_id(self):
        with self.assertRaises(ValueError):
            build_query("example.com", transaction_id=65536)

    def test_parse_response_reads_header_and_answer(self):
        header = struct.pack(HEADER_FORMAT, 42, 0x8180, 1, 1, 0, 0)
        fields = parse_response(header + b"93.184.216.34", expected_transaction_id=42)
        self.assertEqual(fields[0], 42)
        self.assertEqual(fields[1], 0x8180)
        self.assertEqual(fields[-1], "93.184.216.34")

    def test_parse_response_rejects_short_packet(self):
        with self.assertRaises(ValueError):
            parse_response(b"short")

    def test_parse_response_detects_transaction_mismatch(self):
        packet = struct.pack(HEADER_FORMAT, 99, 0x8180, 1, 1, 0, 0) + b"1.2.3.4"
        with self.assertRaises(ValueError):
            parse_response(packet, expected_transaction_id=42)


if __name__ == "__main__":
    unittest.main()
