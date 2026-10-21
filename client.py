import socket
import struct
import sys

SERVER_IP = "10.0.0.1"
SERVER_PORT = 9053


def resolve(domain: str, server_ip: str = SERVER_IP, server_port: int = SERVER_PORT, timeout: float = 2.0):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.settimeout(timeout)

    transaction_id = 1234
    flags = 0x0100  # Standard query with recursion desired
    header = struct.pack("!HHHHHH", transaction_id, flags, 1, 0, 0, 0)
    packet = header + domain.strip().encode()

    try:
        sock.sendto(packet, (server_ip, server_port))
        data, _ = sock.recvfrom(1024)

        if len(data) < 12:
            print("Error: Malformed packet received")
            return

        resp_id, resp_flags, qd, an, ns, ar = struct.unpack("!HHHHHH", data[:12])
        answer = data[12:].decode(errors="ignore")

        if resp_flags == 0x8180:
            print(f"[Transaction ID: {resp_id}] Server response: {answer}")
        elif resp_flags == 0x8183:
            print(f"[Transaction ID: {resp_id}] Error 0x8183 (NXDOMAIN): {answer}")
        else:
            print(f"[Transaction ID: {resp_id}] Server response (flags: {hex(resp_flags)}): {answer}")

    except socket.timeout:
        print("Error: the server is either offline or the packet was lost")
    finally:
        sock.close()


if __name__ == "__main__":
    if len(sys.argv) > 1:
        domain_name = sys.argv[1]
    else:
        domain_name = input("Enter the domain name: ")
    resolve(domain_name)
