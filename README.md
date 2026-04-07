# SDN-Based Firewall using Mininet + POX

## Problem Statement
Implement a controller-based firewall in an SDN environment that blocks or allows
traffic between hosts based on IP and MAC rules, using Mininet and POX controller.

## Topology

h1 (10.0.0.1) ──┐
h2 (10.0.0.2) ──┤── s1 (OVS Switch) ── POX Controller
h3 (10.0.0.3) ──┘   (BLOCKED)

- h1 and h2: allowed to communicate freely
- h3: blocked at switch level via OpenFlow DROP rules

## Setup & Execution

### Requirements
- Ubuntu 20.04+ (or WSL2)
- Mininet 2.3.0
- POX Controller (gar branch)
- Open vSwitch

### Install
```bash
sudo apt install mininet -y
git clone https://github.com/noxrepo/pox.git ~/pox
```

### Run

**Terminal 1 — Start POX controller:**
```bash
cd ~/pox
python3 pox.py log.level --DEBUG misc.firewall_controller
```

**Terminal 2 — Start Mininet topology:**
```bash
sudo python3 topology.py
```

## Test Scenarios

### Scenario 1: Allowed Traffic (h1 → h2)

mininet> h1 ping h2 -c 4

Expected: 0% packet loss

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
