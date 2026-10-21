import socket
import struct

ROOT_IP = "10.0.0.3"
ROOT_PORT = 9053

ex_dns_records = {
    "netflix.com": "192.27.78.9",
    "crunchyroll.com": "89.78.12.0",
    # Fallback records if h1 fails during failover testing
    "example.com": "93.184.216.34",
    "google.com": "142.250.190.46",
    "fedora.org": "8.43.85.67",
}

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((ROOT_IP, ROOT_PORT))

print(f"Secondary/Root DNS server listening on {ROOT_IP}:{ROOT_PORT}.....", flush=True)

while True:
    try:
        data, addr = sock.recvfrom(1024)
    except Exception:
        continue

    # Support ping check if needed
    if data == b"ping":
        sock.sendto(b"pong", addr)
        continue

    if len(data) < 12:
        continue

    header = data[:12]
    payload = data[12:]
    trans_id, flags, qd, an, ns, ar = struct.unpack("!HHHHHH", header)
    domain_requested = payload.decode(errors="ignore").strip()

    if domain_requested in ex_dns_records:
        ip_answer = ex_dns_records[domain_requested]
        resp_header = struct.pack("!HHHHHH", trans_id, 0x8180, 1, 1, 0, 0)
        sock.sendto(resp_header + ip_answer.encode(), addr)
    else:
        # NXDOMAIN: Name does not exist (0x8183)
        resp_header = struct.pack("!HHHHHH", trans_id, 0x8183, 1, 0, 0, 0)
        sock.sendto(resp_header + b"NXDOMAIN: Domain not found", addr)
