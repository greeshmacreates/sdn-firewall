# POX & Mininet Setup Guide

## Prerequisites
This project requires **Linux or Linux subsystem (WSL2)**. It will NOT work on native Windows.

### Option 1: Use WSL2 (Recommended for Windows)
```bash
# In PowerShell as Administrator:
wsl --install

# Then open WSL terminal and:
sudo apt update && sudo apt install -y mininet openvswitch-switch python3-pip
pip install pox
```

### Option 2: Use Linux VM or Native Linux
```bash
sudo apt install mininet openvswitch-switch python3-pip
pip install pox
```

## Running the Project

### Terminal 1 - Start POX Controller
```bash
cd ~/cn_sdn/pox
python pox.py log.level --DEBUG ../controller/firewall.py forwarding.l2_learning
```

### Terminal 2 - Start Mininet
```bash
sudo mn --topo single,4 --controller remote --switch ovsk,protocols=OpenFlow10
```

### Terminal 3 (In Mininet) - Run Tests
```bash
# Test 1: Allowed ping (h1 to h2)
h1 ping -c 4 h2

# Test 2: Blocked ping (h1 to h3 - should fail)
h3 ping -c 4 h1

# Check flow table
sh ovs-ofctl dump-flows s1

# Check firewall logs
sh cat ~/cn_sdn/logs/firewall.log
```

## Expected Results
- **h1 ping h2**: ✅ SUCCESS (not blocked)
- **h1 ping h3**: ❌ BLOCKED (10.0.0.3 is in BLOCKED_IPS list)
- Flow table will show 200-priority rules for blocked IPs
- Firewall logs will record all blocked connections
