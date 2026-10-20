import socket
import struct
sock = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)

sock.bind(('10.0.0.1',9053))
cache={}
dns_records = {
    "example.com": "93.184.216.34",
    "google.com": "142.250.190.46",
    "fedora.org": "8.43.85.67"
}

print("Binary DNS server is listening on 10.0.0.1:9053.....")

while True:
    data,addr = sock.recvfrom(1024)
    if data == b'ping':
        print("Received health check, sending pong...")
        sock.sendto(b'pong', addr)
        continue

    print("Processing DNS request...")
    header  = data[:12]
    answer = data[12:]
    transaction_id,flags,qn,an,ns,ar = struct.unpack('!HHHHHH',header)

    domain_requested = answer.decode().strip()


    if domain_requested in dns_records:
        ip_answer = dns_records[domain_requested]
        resp_header = struct.pack('!HHHHHH',transaction_id,0x8180,1,1,0,0)
        final_packet = resp_header+ip_answer.encode()
        sock.sendto(final_packet,addr)
    elif domain_requested in cache:
        print(f"CACHE HIT: {domain_requested}", flush=True)
        saved_ans = cache[domain_requested]

        # Restore the transaction ID for this request.
        saved_ans = struct.pack('!H', transaction_id) + saved_ans[2:]

        sock.sendto(saved_ans, addr)
    else:
        print(f"CACHE MISS: {domain_requested} — forwarding to secondary", flush=True)
        sock.sendto(data, ('10.0.0.3', 9053))
        h3_response, h3_addr = sock.recvfrom(1024)
        cache[domain_requested] = h3_response
        print(f"CACHED RESPONSE: {domain_requested}", flush=True)
        sock.sendto(h3_response, addr)
