import socket
import struct

sock = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)

sock.bind(('10.0.0.3',9053))

ex_dns_records = {
    
    "netflix.com" : '192.27.78.9',
    "crunchyroll.com" : '89:78:12:0'
}

while True:
    data,addr = sock.recvfrom(1024)
    header = data[:12]
    question = data[12:]
    trans_id,flags,qn,an,ns,ar = struct.unpack('!HHHHHH',header)

    domain_requested = question.decode().strip()
    if domain_requested in ex_dns_records:
        ip_answer = ex_dns_records[domain_requested]
        resp_header = struct.pack('!HHHHHH',trans_id,0x8180,1,1,0,0)
        final_packet = resp_header+ip_answer.encode()
        sock.sendto(final_packet,addr)
    else:
        print(f"Sorry, unable to find {domain_requested}")

    
    



"""• Implement UDP name-resolution queries
• Maintain name-to-IP mappings
• Support multiple resolution servers
• Implement caching
• Handle timeouts
• Detect server failures
• Redirect requests when required
• Measure lookup latency"
"""

