# Test Results Documentation

This folder contains the complete test results and logs for the SDN Firewall project.

## Contents

### 1. **TEST_RESULTS.md** 
Complete summary of all tests run on the Mininet environment

### 2. **allowed_ping.txt**
✅ Successful ping from h1 to h2
- 0% packet loss
- h2 is NOT in blocklist
- Demonstrates allowed traffic

### 3. **blocked_ping.txt** 
❌ Failed ping from h3 to h1
- 100% packet loss
- h3 (10.0.0.3) is in BLOCKED_IPS
- Demonstrates firewall enforcement

### 4. **flow_table.txt**
OpenFlow switch (s1) flow rules dump
- Shows all 4 installed firewall rules
- Displays rule priorities and match criteria
- Shows packet statistics

### 5. **logs.txt**
Raw firewall logs from ~/cn_sdn/logs/firewall.log
- Timestamp of each blocked connection attempt
- Reason for block (IP, MAC, or PORT)
- Defense-in-depth rules verification

## Firewall Rules Applied

| Priority | Match | Action | Purpose |
|----------|-------|--------|---------|
| 200 | nw_src=10.0.0.3 | DROP | Block host h3 by IP |
| 200 | dl_src=00:00:00:00:00:03 | DROP | Block host h3 by MAC |
| 150 | TCP port 80 | DROP | Block HTTP traffic |
| 0 | Any (default) | CONTROLLER | Forward unknown flows to POX |

## Testing Environment

- **Tool**: Mininet 2.3.1
- **Protocol**: OpenFlow 1.0
- **Controller**: POX (Python OpenFlow eXtensible library)
- **Topology**: single,4 (1 switch, 4 hosts)
- **Switch**: Open vSwitch (OVS)

## How to Reproduce

See [SETUP.md](../SETUP.md) for installation and execution instructions.
