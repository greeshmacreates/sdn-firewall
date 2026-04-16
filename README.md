# CN SDN Project - Controller-Based Firewall

**Implement and demonstrate a Software Defined Networking (SDN) firewall that blocks or allows traffic between hosts using rule-based filtering.**

---

## Problem Statement & Requirements

### ✅ Requirement 1: Controller-Based Firewall
**Status: IMPLEMENTED**
- POX OpenFlow controller manages firewall rules centrally
- Rules installed proactively when switch connects
- No need for complex switch configurations
- Centralized management of security policies

### ✅ Requirement 2: Rule-Based Filtering
**Status: IMPLEMENTED**
- **IP-Level Filtering**: Block/allow by source IPv4 address
- **MAC-Level Filtering**: Block/allow by source MAC address  
- **Port-Level Filtering**: Block/allow by destination TCP port
- Three-layer defense-in-depth approach

### ✅ Requirement 3: Install Drop Rules
**Status: IMPLEMENTED**
- OpenFlow DROP rules installed at switch with explicit action
- High priority (200) for IP/MAC rules
- Medium priority (150) for port rules
- Rules evaluated in priority order

### ✅ Requirement 4: Test Allowed vs Blocked Traffic
**Status: IMPLEMENTED**
- Allowed traffic between non-blocked hosts (h1 ↔ h2)
- Blocked traffic from blocked host (h3 ✗)
- ICMP ping tests demonstrate both scenarios
- Flow table dump shows all active rules

### ✅ Requirement 5: Maintain Logs of Blocked Packets
**Status: IMPLEMENTED**
- Timestamped logs of all blocked connections
- Logs recorded when rules are installed
- Logs record rule type (IP/MAC/PORT)
- Source and destination in each log entry
- File: `~/cn_sdn/logs/firewall.log`

---

## Architecture Overview

```
┌─────────────────────────────────────────┐
│           POX FIREWALL CONTROLLER       │
│  (Rules Engine + OpenFlow Orchestration)│
└──────────────┬──────────────────────────┘
               │ OpenFlow Protocol
               │ (Flow Rules Installation)
               ▼
┌─────────────────────────────────────────┐
│   OPEN vSWITCH (s1) - Flow Tables       │
│  ┌─────────────────────────────────────┐│
│  │ Priority 200: IP Filter Rules       ││
│  │ Priority 200: MAC Filter Rules      ││
│  │ Priority 150: Port Filter Rules     ││
│  │ Priority 0:   Controller Fallback   ││
│  └─────────────────────────────────────┘│
└──────────────┬──────────────────────────┘
               │
      ┌────────┴────────┬────────┬────────┐
      ▼                 ▼        ▼        ▼
    ┌──┐              ┌──┐    ┌──┐    ┌──┐
    │h1│   ALLOWED    │h2│    │h3│    │h4│
    │  │◄────────────►│  │    │  │    │  │
    └──┘  10.0.0.1   └──┘   └──┘    └──┘
         10.0.0.2             BLOCKED
                           10.0.0.3 ✗
```

---

## Network Topology

```
Hosts Configuration:
  ├─ h1: 10.0.0.1 (MAC: 00:00:00:00:00:01) → ✅ ALLOWED
  ├─ h2: 10.0.0.2 (MAC: 00:00:00:00:00:02) → ✅ ALLOWED
  ├─ h3: 10.0.0.3 (MAC: 00:00:00:00:00:03) → ❌ BLOCKED
  └─ h4: 10.0.0.4 (MAC: 00:00:00:00:00:04) → ✅ ALLOWED

Firewall Rules Applied:
  1. Priority 200 - Block IP 10.0.0.3 (h3)
  2. Priority 200 - Block MAC 00:00:00:00:00:03 (h3)
  3. Priority 150 - Block TCP port 80 (HTTP)
  4. Priority 150 - Block TCP port 443 (HTTPS)
  5. Priority 150 - Block TCP port 22 (SSH)
  6. Priority 0   - Default: Forward to controller
```

---

## Project Structure

```
cn_sdn/
├── controller/
│   ├── firewall.py      ← Main firewall engine
│   └── rules.py         ← Rule definitions (IP/MAC/Port)
├── logs/
│   └── firewall.log     ← Blocked traffic logs
├── results/             ← Test results & documentation
│   ├── TEST_RESULTS.md
│   ├── allowed_ping.txt
│   ├── blocked_ping.txt
│   ├── flow_table.txt
│   └── logs.txt
├── README.md
├── SETUP.md             ← Installation guide
└── .gitignore
```

---

## Implementation Details

### 1. Firewall Engine (firewall.py)

**Key Components:**
- `_handle_ConnectionUp()` - Installs rules when switch connects
- `install_drop_rule()` - Creates and sends OpenFlow DROP rules
- `write_log()` - Logs all blocked traffic events
- `_handle_PacketIn()` - Monitors packet-in events for debugging

**Rule Installation Sequence:**
```python
1. Switch connects → ConnectionUp event triggered
2. For each BLOCKED_IP:
   - Create flow rule matching source IP
   - Set priority 200 (highest)
   - Set action to DROP
   - Install in switch
   - Log to file

3. For each BLOCKED_MAC:
   - Create flow rule matching source MAC
   - Set priority 200
   - Set action to DROP
   - Install in switch
   - Log to file

4. For each BLOCKED_PORT:
   - Create flow rule matching destination port
   - Set priority 150
   - Set action to DROP
   - Install in switch
   - Log to file
```

### 2. Rule Definitions (rules.py)

```python
BLOCKED_IPS = ['10.0.0.3']           # h3 - completely blocked
BLOCKED_MACS = ['00:00:00:00:00:03'] # Defense-in-depth
BLOCKED_PORTS = [80, 443, 22]        # Service-level blocking
```

### 3. Logging System

**Log Format:**
```
[TIMESTAMP] ACTION | rule=TYPE | src=SOURCE | dst=DESTINATION
```

**Example Logs:**
```
[2026-04-17 14:22:15.123] BLOCKED | rule=IP   | src=10.0.0.3      | dst=*
[2026-04-17 14:22:15.124] BLOCKED | rule=MAC  | src=00:00:00:00:00:03 | dst=*
[2026-04-17 14:22:15.125] BLOCKED | rule=PORT | src=*             | dst=tcp:80
```

---

## Execution Instructions

### Prerequisites
- Linux/WSL2
- Mininet 2.3.0+
- POX (Python OpenFlow eXtensible)
- Open vSwitch

### Setup

```bash
# Install dependencies
sudo apt update
sudo apt install -y mininet openvswitch-switch python3-pip
pip install pox

# Clone POX (if needed)
git clone https://github.com/noxrepo/pox.git ~/pox
```

### Running the Firewall

**Terminal 1 - Start POX Controller:**
```bash
cd ~/pox
python pox.py log.level --DEBUG ../controller/firewall.py forwarding.l2_learning
```

**Terminal 2 - Start Mininet:**
```bash
sudo mn --topo single,4 --controller remote --switch ovsk,protocols=OpenFlow10
```

**Terminal 3 (inside Mininet) - Run Tests:**
```bash
# Test 1: Check connected hosts
mininet> nodes

# Test 2: Allowed traffic (h1 → h2)
mininet> h1 ping h2 -c 4
# Expected: 0% packet loss ✅

# Test 3: Blocked traffic (h3 → h1)
mininet> h3 ping h1 -c 4
# Expected: 100% packet loss ❌

# Test 4: View flow table
mininet> sh ovs-ofctl dump-flows s1

# Test 5: Check logs
mininet> sh cat ~/cn_sdn/logs/firewall.log

# Exit Mininet
mininet> exit
```

---

## Test Results Summary

| Test Case | Source | Destination | Rule Applied | Expected Result | Actual Result |
|-----------|--------|-------------|---------------|-----------------|---------------|
| Allowed Traffic | h1 (10.0.0.1) | h2 (10.0.0.2) | None | ✅ PASS | ✅ PASS |
| Blocked by IP | h3 (10.0.0.3) | h1 (10.0.0.1) | Priority 200 IP | ❌ DROP | ❌ DROP |
| Blocked by MAC | h3 | Any | Priority 200 MAC | ❌ DROP | ❌ DROP |
| Blocked by Port | Any | Port 80 (HTTP) | Priority 150 Port | ❌ DROP | ❌ DROP |

**Detailed test results:** See [results/TEST_RESULTS.md](results/TEST_RESULTS.md)

---

## How to Modify Rules

### Add a Blocked Host

Edit `controller/rules.py`:
```python
BLOCKED_IPS = [
    '10.0.0.3',  # Original
    '10.0.0.5',  # NEW - Add malicious host h5
]

BLOCKED_MACS = [
    '00:00:00:00:00:03',  # Original
    '00:00:00:00:00:05',  # NEW - Add h5's MAC
]
```

### Add a Blocked Port

```python
BLOCKED_PORTS = [
    80, 443, 22,  # Original
    8080,         # NEW - Block alternate web server
    3306,         # NEW - Block MySQL
]
```

### Change Rule Priorities

Edit `controller/firewall.py`:
```python
install_drop_rule(connection, 200, match, reason, src, dst)  # Change 200
```

Then restart POX controller:
```bash
# Kill existing POX
pkill -f pox.py

# Restart
python pox.py log.level --DEBUG ../controller/firewall.py forwarding.l2_learning
```

---

## Key Features Implemented

✅ **Proactive Rule Installation** - Rules installed before any traffic flows  
✅ **Multiple Filtering Layers** - IP, MAC, and Port filtering  
✅ **Explicit DROP Actions** - No ambiguous behavior  
✅ **Priority Levels** - IP/MAC rules (200) checked before Port rules (150)  
✅ **Comprehensive Logging** - Timestamp, rule type, source, destination  
✅ **Easy Rule Management** - Add/modify rules in one file  
✅ **Controller-Based** - Centralized security policy  
✅ **OpenFlow 1.0 Compatible** - Works with standard switches  

---

## Reference Documentation

- [SETUP.md](SETUP.md) - Installation guide
- [PRESENTATION_GUIDE.md](PRESENTATION_GUIDE.md) - **How to run & present the demo** ⭐
- [IMPLEMENTATION_REPORT.md](IMPLEMENTATION_REPORT.md) - Requirement verification
- [results/TEST_RESULTS.md](results/TEST_RESULTS.md) - Detailed test results
- [results/allowed_ping.txt](results/allowed_ping.txt) - Successful ping output
- [results/blocked_ping.txt](results/blocked_ping.txt) - Failed ping output
- [results/flow_table.txt](results/flow_table.txt) - OpenFlow rules dump
- [results/logs.txt](results/logs.txt) - Firewall logs

---

## Summary

This project successfully demonstrates:
1. **Controller-Based Firewall Architecture** using POX and OpenFlow
2. **Rule-Based Filtering** at IP, MAC, and port levels
3. **OpenFlow DROP Rule Installation** with proper priorities
4. **Test Coverage** for both allowed and blocked traffic
5. **Comprehensive Logging** of all firewall actions

All requirements from the problem statement have been fully implemented and tested.

### Scenario 2: Blocked Traffic (h3 → h1)

mininet> h3 ping h1 -c 4

Expected: 100% packet loss — Destination Host Unreachable

### Scenario 3: Throughput Test

mininet> h2 iperf -s -p 5001 &
mininet> h1 iperf -c 10.0.0.2 -p 5001 -t 5   # allowed — high throughput
mininet> h3 iperf -c 10.0.0.1 -p 5001 -t 5   # blocked — connection refused

### Scenario 4: Flow Table Verification

mininet> sh ovs-ofctl dump-flows s1

## Expected Output

### Ping (allowed):

4 packets transmitted, 4 received, 0% packet loss

### Ping (blocked):

4 packets transmitted, 0 received, 100% packet loss

### Flow Table:

priority=100,ip,nw_src=10.0.0.3 actions=drop
priority=100,dl_src=00:00:00:00:00:03 actions=drop

### Firewall Log (`firewall.log`):

[2026-04-07 15:08:46] BLOCKED | reason=RULE_INSTALL | src=10.0.0.3 | dst=N/A
[2026-04-07 15:08:46] BLOCKED | reason=MAC | src=00:00:00:00:00:03 | dst=...

### iperf (allowed h1→h2):

[1] 0.0-5.0 sec  18.4 GBytes  31.5 Gbits/sec

### iperf (blocked h3→h1):

tcp connect failed: No route to host

## Firewall Rules
Defined at the top of `firewall_controller.py`:
```python
BLOCKED_IPS  = ['10.0.0.3']
BLOCKED_MACS = ['00:00:00:00:00:03']
```

## References
- [Mininet Docs](http://mininet.org)
- [POX Controller Wiki](https://noxrepo.github.io/pox-doc/html/)
- [OpenFlow 1.0 Spec](https://opennetworking.org/wp-content/uploads/2013/04/openflow-spec-v1.0.0.pdf)
- [OVS Documentation](https://www.openvswitch.org)
>>>>>>> 986ada43d5666b87dd84f8ed5c48964630fe401b
