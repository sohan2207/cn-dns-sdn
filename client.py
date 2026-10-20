import socket
import struct

sock  = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
sock.settimeout(2.0)

domain = input("Enter the domain name")
transaction_id = 1234
flags = 0x0100
header  = struct.pack("!HHHHHH",transaction_id,flags,1,0,0,0)
packet = header + domain.encode()


sock.sendto(packet,("10.0.0.1",9053))
try:
    data,addr = sock.recvfrom(1024)
    resp_header = data[:12]
    resp_id,resp_flags,qd,an,ns,ar = struct.unpack('!HHHHHH',resp_header)
    answer = data[12:].decode()
    print(f"[Transaction ID: {resp_id}] Server response: {answer}")
except socket.timeout:
    print("Error: the server is either offline or the packet was lost")