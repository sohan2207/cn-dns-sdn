"""Health-check the primary DNS service and install SDN failover rules.

Can be run standalone while Mininet is active. Set MININET_H2_PID to the
persistent Mininet h2 shell PID to avoid process-name discovery.
"""
import os
import subprocess
import time


def get_h2_pid():
    configured_pid = os.environ.get("MININET_H2_PID")
    if configured_pid and configured_pid.isdigit() and os.path.exists(f"/proc/{configured_pid}"):
        return configured_pid

    result = subprocess.run(
        ["pgrep", "-f", r"bash --norc --noediting -is mininet:h2"],
        capture_output=True, text=True,
    )
    for pid in result.stdout.splitlines():
        if pid.isdigit() and os.path.exists(f"/proc/{pid}"):
            return pid
    raise RuntimeError("Could not find Mininet h2. Start the topology first.")


def check_server_health(ip, port, h2_pid):
    probe = (
        "import socket; "
        "s=socket.socket(socket.AF_INET,socket.SOCK_DGRAM); "
        "s.settimeout(2); "
        f"s.sendto(b'ping',('{ip}',{port})); "
        "print(s.recvfrom(1024)[0].decode()); s.close()"
    )
    try:
        result = subprocess.run(
            ["mnexec", "-a", str(h2_pid), "python3", "-c", probe],
            capture_output=True, text=True, timeout=3,
        )
        return result.returncode == 0 and "pong" in result.stdout
    except (subprocess.TimeoutExpired, OSError):
        return False


def install_failover_rules():
    rules = [
        ['ovs-ofctl', 'add-flow', 's1',
         'priority=100,udp,nw_dst=10.0.0.1,tp_dst=9053,actions=mod_nw_dst:10.0.0.3,mod_dl_dst:00:00:00:00:00:03,normal'],
        ['ovs-ofctl', 'add-flow', 's1',
         'priority=100,udp,nw_src=10.0.0.3,tp_src=9053,actions=mod_nw_src:10.0.0.1,normal'],
    ]
    for rule in rules:
        result = subprocess.run(rule, capture_output=True, text=True)
        if result.returncode:
            print(f"Failed to install flow: {result.stderr.strip()}", flush=True)
            return False
    print("Failover rules installed.", flush=True)
    return True


def run_controller():
    h2_pid = get_h2_pid()
    print(f"Monitoring primary DNS (h1) using h2 PID {h2_pid}", flush=True)
    missed_pings = 0
    while True:
        if not check_server_health('10.0.0.1', 9053, h2_pid):
            missed_pings += 1
            print(f"Missed ping {missed_pings} from h1...", flush=True)
            if missed_pings >= 2:
                print("h1 appears down. Installing failover rules...", flush=True)
                install_failover_rules()
                return
        else:
            missed_pings = 0
            print("Primary DNS is healthy.", flush=True)
        time.sleep(3)


if __name__ == '__main__':
    run_controller()
