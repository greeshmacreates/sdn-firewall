"""
Firewall Rules Configuration
=============================
Define which hosts, MACs, and ports should be blocked by the firewall.

Network Topology:
  h1 (10.0.0.1) → ALLOWED
  h2 (10.0.0.2) → ALLOWED  
  h3 (10.0.0.3) → BLOCKED  ← h3 is the malicious host
  h4 (10.0.0.4) → ALLOWED

What Gets Logged:
================
1. RULE INSTALLATION (When controller connects)
   [timestamp] BLOCKED | rule=IP | src=10.0.0.3 | dst=*
   [timestamp] BLOCKED | rule=MAC | src=00:00:00:00:00:03 | dst=*
   [timestamp] BLOCKED | rule=PORT | src=* | dst=tcp:80

2. BLOCKED PACKETS (When h3 tries to send)
   [timestamp] DROPPED | rule=IP | src=10.0.0.3 | dst=10.0.0.1 | info=Protocol_1
   
3. BLOCKED PORT ACCESS
   [timestamp] DROPPED | rule=PORT | src=10.0.0.1 | dst=tcp:80 | info=Port_blocked
   
All logs are written to: ~/cn_sdn/logs/firewall.log
"""

# ═══════════════════════════════════════════════════════════════════
# BLOCKED IP ADDRESSES
# ═══════════════════════════════════════════════════════════════════
# Hosts with these source IPs will have all traffic dropped
# At Priority 200 (high priority)
# 
# LOGGING: When this rule matches, logs:
#   [timestamp] DROPPED | rule=IP | src=10.0.0.3 | dst=<dest_ip> | info=<protocol>
BLOCKED_IPS = [
    '10.0.0.3',  # h3 - malicious host (blocked completely)
]

# ═══════════════════════════════════════════════════════════════════
# BLOCKED MAC ADDRESSES  
# ═══════════════════════════════════════════════════════════════════
# Hosts with these source MACs will have all traffic dropped
# Provides defense-in-depth in case IP is spoofed
# At Priority 200 (high priority)
#
# LOGGING: When this rule matches, logs:
#   [timestamp] DROPPED | rule=MAC | src=00:00:00:00:00:03 | dst=<dest_mac>
BLOCKED_MACS = [
    '00:00:00:00:00:03',  # MAC of h3
]

# ═══════════════════════════════════════════════════════════════════
# BLOCKED PORTS (TCP)
# ═══════════════════════════════════════════════════════════════════
# Any TCP traffic destined to these ports will be dropped
# Useful for blocking vulnerable services
# At Priority 150 (medium priority)
#
# LOGGING: When this rule matches, logs:
#   [timestamp] DROPPED | rule=PORT | src=<src_ip> | dst=tcp:80 | info=Port_blocked
BLOCKED_PORTS = [
    80,    # HTTP - Block web servers
    443,   # HTTPS - Block secure web servers  
    22,    # SSH - Block remote access
]

# ═══════════════════════════════════════════════════════════════════
# CONFIGURATION NOTES
# ═══════════════════════════════════════════════════════════════════
# Priority Levels:
#   200 = IP/MAC rules (highest - checked first)
#   150 = Port rules
#     0 = Default controller rule (lowest)
#
# Order of Evaluation:
#   1. Check blocked source IP (priority 200)
#   2. Check blocked source MAC (priority 200)
#   3. Check blocked destination port (priority 150)
#   4. If no match → forward to controller for learning
#
# Log File Location:
#   ~/cn_sdn/logs/firewall.log
#   Auto-created by controller on startup
#
# Log Format:
#   [YYYY-MM-DD HH:MM:SS.mmm] ACTION | rule=TYPE | src=SOURCE | dst=DESTINATION | info=EXTRA
#
# To add more blocked hosts:
#   1. Add IP to BLOCKED_IPS
#   2. Add corresponding MAC to BLOCKED_MACS
#   3. Restart POX controller
#   4. Check logs: tail -f ~/cn_sdn/logs/firewall.log