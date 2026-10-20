
#!/usr/bin/env bash
set -uo pipefail
cd "$(dirname "$0")"

REPORT_DIR="reports"
TIMESTAMP="$(date +%Y%m%d_%H%M%S)"
REPORT="$REPORT_DIR/test_report_$TIMESTAMP.txt"
mkdir -p "$REPORT_DIR"

PASS=0
FAIL=0
TOPOLOGY_PID=""
CONTROLLER_PID=""

pass() { echo "[PASS] $1"; PASS=$((PASS + 1)); }
fail() { echo "[FAIL] $1"; FAIL=$((FAIL + 1)); }

cleanup() {
    echo
    echo "Cleaning up..."
    if [[ -n "$CONTROLLER_PID" ]]; then
        kill "$CONTROLLER_PID" 2>/dev/null || true
    fi
    if [[ -n "$TOPOLOGY_PID" ]]; then
        kill "$TOPOLOGY_PID" 2>/dev/null || true
        wait "$TOPOLOGY_PID" 2>/dev/null || true
    fi
    mn -c >/dev/null 2>&1 || true
}
trap cleanup EXIT INT TERM

exec > >(tee "$REPORT") 2>&1

echo "DNS-like SDN test run: $TIMESTAMP"
echo "Repository: $(pwd)"
echo

for cmd in mn ovs-ofctl mnexec python3 timeout; do
    if command -v "$cmd" >/dev/null 2>&1; then
        pass "Prerequisite $cmd"
    else
        fail "Missing prerequisite $cmd"
    fi
done

if (( FAIL )); then
    echo "Install missing prerequisites before continuing."
    exit 1
fi

echo
echo "Checking Python tests..."
if python3 -m unittest discover -s tests -p 'test_protocol_helpers.py' -v; then
    pass "Protocol unit tests"
else
    fail "Protocol unit tests"
fi

echo
echo "Starting clean Mininet topology..."
mn -c >/dev/null 2>&1 || true
sudo -n true 2>/dev/null || {
    echo "Run this script with sudo: sudo bash ./run_all_tests.sh"
    exit 1
}

sudo python3 topology.py > /tmp/cn_topology.log 2>&1 &
TOPOLOGY_PID=$!

# Wait for Mininet host shells to appear.
H2_PID=""
for _ in $(seq 1 30); do
    H2_PID="$(pgrep -f 'bash --norc --noediting -is mininet:h2' | head -n1 || true)"
    if [[ -n "$H2_PID" ]] && sudo test -d "/proc/$H2_PID"; then
        break
    fi
    sleep 1
done

if [[ -z "$H2_PID" ]]; then
    fail "Mininet h2 host did not start"
    cat /tmp/cn_topology.log
    exit 1
fi
pass "Mininet topology started (h2 PID $H2_PID)"

# Start DNS services inside the host namespaces.
sudo mnexec -a "$H2_PID" python3 -c \
    "import subprocess; subprocess.Popen(['python3','-u','server.py'], stdout=open('/tmp/server.log','w'), stderr=subprocess.STDOUT)" \
    || true

H1_PID="$(pgrep -f 'bash --norc --noediting -is mininet:h1' | head -n1 || true)"
H3_PID="$(pgrep -f 'bash --norc --noediting -is mininet:h3' | head -n1 || true)"

if [[ -z "$H1_PID" || -z "$H3_PID" ]]; then
    fail "Could not locate h1/h3 namespaces"
    exit 1
fi

sudo mnexec -a "$H3_PID" python3 -c \
    "import subprocess; subprocess.Popen(['python3','-u','root.py'], stdout=open('/tmp/root.log','w'), stderr=subprocess.STDOUT)" \
    || true

sleep 2

# Verify primary and secondary listeners.
if sudo mnexec -a "$H1_PID" python3 -c \
    "import socket; s=socket.socket(socket.AF_INET,socket.SOCK_DGRAM); s.settimeout(1); s.sendto(b'ping',('10.0.0.1',9053)); assert s.recvfrom(1024)[0] == b'pong'; s.close()"; then
    pass "Primary DNS health check"
else
    fail "Primary DNS health check"
fi

if sudo mnexec -a "$H3_PID" python3 -c \
    "import socket; s=socket.socket(socket.AF_INET,socket.SOCK_DGRAM); s.bind(('10.0.0.3',9053)); s.close()" 2>/dev/null; then
    fail "Secondary DNS listener check (port appears free)"
else
    pass "Secondary DNS listener check"
fi

echo
echo "Running primary DNS benchmarks..."
if sudo mnexec -a "$H2_PID" python3 benchmark.py --host 10.0.0.1 --port 9053 --domain example.com --count 30; then
    pass "Primary benchmark"
else
    fail "Primary benchmark"
fi

echo
echo "Running secondary-forwarding benchmark..."
if sudo mnexec -a "$H2_PID" python3 benchmark.py --host 10.0.0.1 --port 9053 --domain netflix.com --count 30; then
    pass "Forwarding benchmark"
else
    fail "Forwarding benchmark"
fi

echo
echo "Starting controller..."
sudo python3 sdncontroller.py > /tmp/cn_controller.log 2>&1 &
CONTROLLER_PID=$!
sleep 5

if grep -q "Primary DNS is healthy" /tmp/cn_controller.log; then
    pass "Controller detects healthy primary"
else
    fail "Controller healthy-primary check"
fi

echo
echo "Stopping primary DNS process to simulate failure..."
sudo mnexec -a "$H1_PID" pkill -f 'python3 -u server.py' || true
sleep 8

if grep -q "Failover rules installed" /tmp/cn_controller.log; then
    pass "Controller installed failover rules"
else
    fail "Controller did not install failover rules"
    cat /tmp/cn_controller.log
fi

echo
echo "Testing query through primary IP while primary is down..."
if sudo mnexec -a "$H2_PID" python3 -c \
    "import sys; sys.path.insert(0,'.'); from tests.protocol_helpers import query_once; r=query_once('10.0.0.1',9053,'netflix.com',3,54321); print(r); assert r.answer == '192.27.78.9'"; then
    pass "Failover query answered by secondary"
else
    fail "Failover query"
fi

echo
echo "Controller log:"
cat /tmp/cn_controller.log 2>/dev/null || true

echo
echo "======================================"
echo "FINAL RESULTS: $PASS passed, $FAIL failed"
echo "Report: $REPORT"
echo "======================================"

(( FAIL == 0 ))

