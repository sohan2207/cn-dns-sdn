"""Helpers for the project's current simplified UDP message format.

Current format (as implemented in the shared starter files):
    request  = 12-byte network-order header + UTF-8 domain name
    response = 12-byte network-order header + UTF-8 answer text

This is a project-specific test protocol, not standard DNS wire format.
"""

import socket
import struct
import time
from typing import NamedTuple
from typing import Optional

HEADER_FORMAT = "!HHHHHH"
HEADER_SIZE = 12


class DNSLikeResponse(NamedTuple):
    transaction_id: int
    flags: int
    question_count: int
    answer_count: int
    authority_count: int
    additional_count: int
    answer: str
    latency_ms: float


def build_query(domain: str, transaction_id: int = 1234) -> bytes:
    """Build a query using the simplified protocol used by the starter code."""
    if not domain or not domain.strip():
        raise ValueError("domain must not be empty")
    if not 0 <= transaction_id <= 65535:
        raise ValueError("transaction_id must fit in an unsigned 16-bit integer")

    header = struct.pack(HEADER_FORMAT, transaction_id, 0x0100, 1, 0, 0, 0)
    return header + domain.strip().encode("utf-8")


def parse_response(
    packet: bytes,
    expected_transaction_id: Optional[int] = None
) -> tuple:
    """Parse the simplified response header and text answer."""
    if len(packet) < HEADER_SIZE:
        raise ValueError(f"response is shorter than {HEADER_SIZE} bytes")

    fields = struct.unpack(HEADER_FORMAT, packet[:HEADER_SIZE])
    if expected_transaction_id is not None and fields[0] != expected_transaction_id:
        raise ValueError(
            f"transaction ID mismatch: expected {expected_transaction_id}, received {fields[0]}"
        )

    answer = packet[HEADER_SIZE:].decode("utf-8", errors="replace")
    return (*fields, answer)


def query_once(host: str, port: int, domain: str, timeout_s: float = 2.0,
               transaction_id: int = 1234) -> DNSLikeResponse:
    """Send one query and return the answer and measured round-trip latency."""
    packet = build_query(domain, transaction_id)
    started = time.perf_counter()

    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
        sock.settimeout(timeout_s)
        sock.sendto(packet, (host, port))
        response, _peer = sock.recvfrom(4096)

    elapsed_ms = (time.perf_counter() - started) * 1000
    fields = parse_response(response, expected_transaction_id=transaction_id)
    return DNSLikeResponse(*fields, latency_ms=elapsed_ms)
