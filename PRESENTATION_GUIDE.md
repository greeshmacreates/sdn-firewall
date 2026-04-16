# 🎯 SDN Firewall - Presentation & Execution Guide

**How to Run & Present Your Project**

---

## 📋 QUICK START (5 mins to working demo)

### Prerequisites Check
```bash
# Verify you have everything
mininet --version              # Should be 2.3.0 or higher
python3 --version              # Should be 3.6+
ls ~/pox                        # POX should be installed
ls ~/cn_sdn                     # Project files should exist
```

---

## 🚀 PHASE 1: Setup (Do this first, takes ~2 mins)

### Terminal 1: Start POX Controller
```bash
cd ~/pox
python pox.py log.level --DEBUG ../controller/firewall.py forwarding.l2_learning
```

**What to expect:**
```
╔════════════════════════════════════════╗
║  🔥 SDN FIREWALL CONTROLLER STARTED  ║
║  POX-Based Rule Engine                ║
╚════════════════════════════════════════╝

✓ Listeners registered
✓ Waiting for switch connections...
```

**✅ WHEN YOU SEE THIS → Controller is ready for connections**

---

### Terminal 2: Start Mininet Topology
```bash
sudo mn --topo single,4 --controller remote --switch ovsk,protocols=OpenFlow10
```

**What to expect:**
```
*** Creating network
*** Adding controller
*** Adding hosts and switches
*** Adding links
*** Starting network
*** Configuring hosts
mininet>
```

**⚠️ IMPORTANT:** Look at Terminal 1 → You should see:
```
[CONNECT] Switch connected: 00:00:00:00:00:00:00:01
════════════════════════════════════════
Installing firewall rules...
✓ DROP rule installed: IP (Priority: 200)
✓ DROP rule installed: MAC (Priority: 200)
✓ DROP rule installed: PORT (Priority: 150)
✓ DROP rule installed: PORT (Priority: 150)
✓ DROP rule installed: PORT (Priority: 150)
════════════════════════════════════════
[OK] All 8 rules installed
```

**✅ WHEN YOU SEE THIS → Firewall rules are active!**

---

## 🧪 PHASE 2: Testing (The Demo Part - takes ~3 mins)

### In Terminal 2 (Mininet prompt): Run these commands in order

#### STEP 1: Show network topology
```bash
mininet> nodes
available nodes are:
c0 h1 h2 h3 h4 s1
```

#### STEP 2: Show host details
```bash
mininet> net
h1-eth0:s1-eth1
h2-eth0:s1-eth2
h3-eth0:s1-eth3
h4-eth0:s1-eth4
s1-tmp: c0-eth0
```

#### STEP 3: Ping all hosts (Check connectivity)
```bash
mininet> pingall
h1 -> h2 h4
h2 -> h1 h4
h3 -> X X X X
h4 -> h1 h2
```

**What to say in presentation:**
> "Notice: h3 cannot ping anyone. That's because h3 (10.0.0.3) is completely blocked by our firewall rules."

---

#### STEP 4: Test 1 - ALLOWED TRAFFIC ✅
```bash
mininet> h1 ping -c 4 h2
```

**Expected output:**
```
PING 10.0.0.2 (10.0.0.2) from 10.0.0.1
56(84) bytes of ICMP seq=1 time=0.441 ms
56(84) bytes of ICMP seq=2 time=0.123 ms
56(84) bytes of ICMP seq=3 time=0.087 ms
56(84) bytes of ICMP seq=4 time=0.095 ms
--- 10.0.0.2 statistics ---
4 packets transmitted, 4 received, 0% packet loss
```

**📸 SCREENSHOT 1: Allowed Traffic**

**What to say:**
> "TEST 1: ALLOWED TRAFFIC ✅
> - h1 pinging h2
> - Both hosts are NOT blocked
> - 4/4 packets received = 0% packet loss
> - Communication is ALLOWED"

---

#### STEP 5: Test 2 - BLOCKED TRAFFIC ❌
```bash
mininet> h3 ping -c 4 h1
```

**Expected output:**
```
PING 10.0.0.1 (10.0.0.1) from 10.0.0.3
--- 10.0.0.1 statistics ---
4 packets transmitted, 0 received, 100% packet loss, time 3056ms
```

**📸 SCREENSHOT 2: Blocked Traffic**

**What to say:**
> "TEST 2: BLOCKED TRAFFIC ❌
> - h3 pinging h1
> - h3 (10.0.0.3) is in our BLOCKED_IPS list
> - 0/4 packets received = 100% packet loss
> - Communication is BLOCKED by firewall rule"

---

#### STEP 6: Show OpenFlow Rules
```bash
mininet> sh ovs-ofctl dump-flows s1
```

**Expected output:**
```
NXST_FLOW reply (xid=0x4):
 cookie=0x0, duration=45s, table=0, priority=200, dl_type=0x0800, nw_src=10.0.0.3, actions=drop
 cookie=0x0, duration=44s, table=0, priority=200, dl_src=00:00:00:00:00:03, actions=drop
 cookie=0x0, duration=43s, table=0, priority=150, dl_type=0x0800, nw_proto=6, tp_dst=80, actions=drop
 cookie=0x0, duration=42s, table=0, priority=150, dl_type=0x0800, nw_proto=6, tp_dst=443, actions=drop
 cookie=0x0, duration=41s, table=0, priority=150, dl_type=0x0800, nw_proto=6, tp_dst=22, actions=drop
 cookie=0x0, duration=40s, table=0, priority=0, n_packets=248, n_bytes=22156, actions=CONTROLLER:65535
```

**📸 SCREENSHOT 3: Flow Table**

**What to say:**
> "FLOW TABLE - This is the OpenFlow switch memory:
> - PRIORITY 200 rules: Block IP 10.0.0.3 & MAC 00:00:00:00:00:03
> - PRIORITY 150 rules: Block TCP ports 80, 443, 22
> - PRIORITY 0: Default rule - forward unmatched to controller
> - 248 packets have been processed through the controller rule"

---

#### STEP 7: Show Firewall Logs
```bash
mininet> sh cat ~/cn_sdn/logs/firewall.log
```

**Expected output:**
```
[2026-04-17 14:22:15.123] BLOCKED | rule=IP   | src=10.0.0.3      | dst=*
[2026-04-17 14:22:15.124] BLOCKED | rule=MAC  | src=00:00:00:00:00:03 | dst=*
[2026-04-17 14:22:15.125] BLOCKED | rule=PORT | src=*             | dst=tcp:80
[2026-04-17 14:22:15.126] BLOCKED | rule=PORT | src=*             | dst=tcp:443
[2026-04-17 14:22:15.127] BLOCKED | rule=PORT | src=*             | dst=tcp:22
```

**📸 SCREENSHOT 4: Logs**

**What to say:**
> "FIREWALL LOGS - Every blocked connection is logged:
> - Timestamp: Exact time the rule was installed
> - Rule type: IP, MAC, or PORT
> - Source: Where traffic came from
> - Destination: Where it was going
> - Helps audit and troubleshoot security events"

---

#### STEP 8: Exit Mininet
```bash
mininet> exit
```

---

## 📊 PRESENTATION FLOW (What to say)

### Introduction (30 seconds)
```
"This is an SDN-based firewall controller using POX framework.
The firewall implements centralized security management
by installing OpenFlow rules directly at the switch level.
This demonstrates enterprise-grade network security."
```

### Architecture (1 minute)
```
"System consists of three components:
1. POX Controller - Manages firewall rules
2. Open vSwitch - Enforces DROP rules
3. Mininet hosts - Test traffic sources

Rules are installed in three layers:
- IP Layer: Block specific source IPs
- MAC Layer: Block specific source MACs
- Port Layer: Block specific TCP ports
```

### Demo Flow (3 minutes)
```
1. Show topology
2. Demonstrate allowed traffic (h1 to h2) - SUCCESS ✅
3. Demonstrate blocked traffic (h3) - BLOCKED ❌
4. Show OpenFlow flow table
5. Display firewall logs
```

### Results (1 minute)
```
"Results demonstrate:
✅ ALLOWED TRAFFIC: h1 ↔ h2 works perfectly
❌ BLOCKED TRAFFIC: h3 is completely isolated
✅ RULES ENFORCED: 8 flow rules active at switch
✅ LOGGING: All events timestamped and recorded
```

---

## 🎬 PRESENTATION TIPS

### Visual Layout
```
Terminal 1 (POX Controller)
┌─────────────────────────────────────┐
│ Controller logs & status messages   │
│ Shows when rules are installed      │
└─────────────────────────────────────┘

Terminal 2 (Mininet / Tests)
┌─────────────────────────────────────┐
│ Test commands and output            │
│ Shows ping success/failure          │
└─────────────────────────────────────┘

Presenter Screen (Your notes)
┌─────────────────────────────────────┐
│ Key points to mention               │
│ Results to highlight                │
└─────────────────────────────────────┘
```

### Screenshots to Take

1. **Allowed Ping Success** - Show 0% packet loss
2. **Blocked Ping Failure** - Show 100% packet loss
3. **Flow Table Dump** - Show all 8 rules
4. **Firewall Logs** - Show timestamps and rules

### What to Emphasize

✅ **Success Points:**
- Controller installed rules proactively
- No switch configuration needed
- Rules work immediately
- Logs prove enforcement

❌ **Security Points:**
- h3 completely isolated
- Multiple filtering layers
- High-priority rules checked first
- Everything auditable

---

## 🔧 Troubleshooting During Demo

### If POX doesn't start:
```bash
# Make sure you're in the pox directory
cd ~/pox

# Check Python version
python --version  # Should be 3.6+

# Try again
python pox.py log.level --DEBUG ../controller/firewall.py forwarding.l2_learning
```

### If Mininet doesn't connect:
```bash
# In new terminal, check controller status
netstat -tlnp | grep 6633  # Should show POX listening

# Make sure POX is still running
ps aux | grep pox
```

### If tests fail:
```bash
# Inside Mininet, check if controller is connected
mininet> sh ovs-vsctl show

# Should show controller listed
# If not, restart Mininet with proper parameters
```

### If rules aren't showing:
```bash
# Check if rules were installed at all
mininet> sh ovs-ofctl dump-flows s1

# If empty, check POX console for errors
# May need to restart both
```

---

## ⏱️ TIMING BREAKDOWN

| Phase | Time | What to Do |
|-------|------|-----------|
| Setup POX | 30s | Start Terminal 1 |
| Setup Mininet | 30s | Start Terminal 2 |
| Introduction | 30s | Explain project |
| Allowed Test | 30s | h1 ping h2 |
| Blocked Test | 30s | h3 ping h1 |
| Flow Table | 30s | Show rules |
| Logs | 30s | Show audit trail |
| Summary | 30s | Key results |
| **TOTAL** | **~5 mins** | Full demo |

---

## 📝 TALKING POINTS

### When showing Allowed Traffic:
> "As you see, h1 successfully pings h2 with 0% packet loss. 
> Both hosts are not in our blocked list, so traffic passes through normally.
> The firewall learns the path using L2 learning forwarding."

### When showing Blocked Traffic:
> "Now h3 tries to ping h1. Notice 100% packet loss.
> Host h3 is on the BLOCKED_IPS list with IP 10.0.0.3.
> The firewall immediately drops all outgoing packets from h3.
> This happens at the switch level, not at the controller."

### When showing Flow Table:
> "Here are all the OpenFlow rules installed in the switch.
> Priority 200 rules check first - blocking h3's IP and MAC.
> Priority 150 rules check next - blocking vulnerable TCP ports.
> Priority 0 is the fallback - whatever matches here goes to controller."

### When showing Logs:
> "Every blocked rule is logged with timestamp and details.
> This creates an audit trail for security compliance.
> In a real network, these logs would be forwarded to SIEM.
> This is enterprise-grade firewall functionality."

---

## 🎓 Expected Questions & Answers

**Q: Why use both IP and MAC filtering?**
A: "Defense-in-depth. If someone spoofs the IP, we still block by MAC. 
If they spoof both, we block the port. Multiple layers of security."

**Q: Can we add/remove rules dynamically?**
A: "Yes! Edit controller/rules.py and restart POX. 
Rules are applied immediately when the switch reconnects."

**Q: How does this scale to real networks?**
A: "In production, rules come from a central policy server.
Thousands of switches can be managed from one controller.
This is how enterprise SDN firewalls work."

**Q: What if h4 tries to access port 80?**
A: "Any host trying to access port 80 will be blocked.
The port-level rule has priority 150, so it applies to everyone."

---

## 🏁 QUICK CHECKLIST

Before presenting:
- [ ] POX is running and showing "Waiting for switch connections..."
- [ ] Mininet is running and showing "mininet>" prompt
- [ ] Controller shows "All rules installed" message
- [ ] Test: `pingall` shows h3 has X marks
- [ ] Test: `h1 ping h2 -c 4` shows 0% loss
- [ ] Test: `h3 ping h1 -c 4` shows 100% loss
- [ ] Command ready: `sh ovs-ofctl dump-flows s1`
- [ ] Command ready: `sh cat ~/cn_sdn/logs/firewall.log`
- [ ] Screenshots prepared for each step

---

## Summary Commands Quick Reference

```bash
# Copy-paste friendly command sequence

# Terminal 1:
cd ~/pox
python pox.py log.level --DEBUG ../controller/firewall.py forwarding.l2_learning

# Terminal 2:
sudo mn --topo single,4 --controller remote --switch ovsk,protocols=OpenFlow10

# Terminal 2 (inside Mininet) - Run these in order:
nodes
net
pingall
h1 ping -c 4 h2
h3 ping -c 4 h1
sh ovs-ofctl dump-flows s1
sh cat ~/cn_sdn/logs/firewall.log
exit
```

---

**🎉 You're ready to present! Good luck!**
