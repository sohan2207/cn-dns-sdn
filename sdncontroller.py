import socket
import time
import subprocess

def check_server_health(ip,port):
    sock = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
    sock.settimeout(2.0)

    try:
        sock.sendto(b'ping',(ip,port))

        sock.recvfrom(1024)
        return True
    except socket.timeout:
        return False
    finally:
        sock.close()



def run_controller():
    print("Monitoring primary dns(h1)")
    missed_pings = 0
    while True:
        
        if not check_server_health('10.0.0.1',9053):
            missed_pings+=1
            print(f"Missed ping {missed_pings} from h1...")
            if missed_pings>=2:
                print("h1 is down. Pushing openflow rules to s1...")
                subprocess.run('ovs-ofctl add-flow s1 "priority=100,udp,nw_dst=10.0.0.1,tp_dst=9053,actions=mod_nw_dst:10.0.0.3,mod_dl_dst=00:00:00:00:00:03,normal"',shell = True)
                subprocess.run('ovs-ofctl add-flow s1 "priority=100,udp,nw_src=10.0.0.3,tp_src=9053,actions=mod_nw_src:10.0.0.1,normal"',shell = True)
                break
        else:
            missed_pings = 0
        time.sleep(3)


if __name__ == '__main__':
    run_controller()