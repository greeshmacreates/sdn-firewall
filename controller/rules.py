"""
Firewall Rules Configuration
=============================
Define which hosts, MACs, and ports should be blocked by the firewall.

Network Topology:
  h1 (10.0.0.1) → ALLOWED
  h2 (10.0.0.2) → ALLOWED  
  h3 (10.0.0.3) → BLOCKED  ← h3 is the malicious host
  h4 (10.0.0.4) → ALLOWED
"""

# ═══════════════════════════════════════════════════════════════════
# BLOCKED IP ADDRESSES
# ═══════════════════════════════════════════════════════════════════
# Hosts with these source IPs will have all traffic dropped
# At Priority 200 (high priority)
BLOCKED_IPS = [
    '10.0.0.3',  # h3 - malicious host (blocked completely)
]

# ═══════════════════════════════════════════════════════════════════
# BLOCKED MAC ADDRESSES  
# ═══════════════════════════════════════════════════════════════════
# Hosts with these source MACs will have all traffic dropped
# Provides defense-in-depth in case IP is spoofed
# At Priority 200 (high priority)
BLOCKED_MACS = [
    '00:00:00:00:00:03',  # MAC of h3
]

# ═══════════════════════════════════════════════════════════════════
# BLOCKED PORTS (TCP)
# ═══════════════════════════════════════════════════════════════════
# Any TCP traffic destined to these ports will be dropped
# Useful for blocking vulnerable services
# At Priority 150 (medium priority)
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
#   4. If no match → forward to controller for L2 learning
#
# To add more blocked hosts:
#   - Add IP to BLOCKED_IPS
#   - Add corresponding MAC to BLOCKED_MACS
#   - Restart POX controller