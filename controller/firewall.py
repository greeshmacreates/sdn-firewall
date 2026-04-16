"""
SDN-Based Firewall Controller using POX Framework
=================================================
Implements rule-based filtering for IP, MAC, and Port-level traffic control.

Features:
- IP-based blocking (source IP filtering)
- MAC-based blocking (source MAC filtering)  
- Port-based blocking (TCP destination port filtering)
- Explicit DROP actions on blocked flows
- Comprehensive logging of all blocked traffic
- L2 learning for allowed traffic
"""

from pox.core import core
from pox.lib.addresses import IPAddr, EthAddr
from pox.lib.util import dpid_to_str
import pox.openflow.libopenflow_01 as of
from datetime import datetime
import os

log = core.getLogger()

from controller.rules import BLOCKED_IPS, BLOCKED_MACS, BLOCKED_PORTS

LOG_FILE = os.path.expanduser("~/cn_sdn/logs/firewall.log")

def write_log(reason, src, dst, action="BLOCKED"):
    """Log blocked packet information with timestamp"""
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
    line = f"[{ts}] {action:8} | rule={reason:6} | src={src:15} | dst={dst:15}\n"
    
    try:
        with open(LOG_FILE, 'a') as f:
            f.write(line)
    except Exception as e:
        log.error(f"Failed to write log: {e}")
    
    log.warning(line.strip())

def install_drop_rule(connection, priority, match_criteria, reason, src, dst):
    """Install a DROP rule at the switch"""
    msg = of.ofp_flow_mod()
    msg.priority = priority
    
    # Apply match criteria
    for key, value in match_criteria.items():
        setattr(msg.match, key, value)
    
    # Explicitly set NO actions = DROP (implicit drop)
    msg.actions = []
    
    connection.send(msg)
    write_log(reason, src, dst)
    log.info(f"✓ DROP rule installed: {reason} (Priority: {priority})")

def _handle_ConnectionUp(event):
    """Called when a switch connects to the controller"""
    dpid = dpid_to_str(event.connection.dpid)
    log.info(f"[CONNECT] Switch connected: {dpid}")
    log.info("════════════════════════════════════════")
    log.info("Installing firewall rules...")
    
    connection = event.connection
    
    # ═══════════════════════════════════════════════════════════════
    # RULE 1: BLOCK by SOURCE IP (Priority 200)
    # ═══════════════════════════════════════════════════════════════
    for ip in BLOCKED_IPS:
        match = {
            'dl_type': 0x0800,  # IPv4
            'nw_src': IPAddr(ip)
        }
        install_drop_rule(connection, 200, match, "IP", ip, "*")
    
    # ═══════════════════════════════════════════════════════════════
    # RULE 2: BLOCK by SOURCE MAC (Priority 200)
    # ═══════════════════════════════════════════════════════════════
    for mac in BLOCKED_MACS:
        match = {
            'dl_src': EthAddr(mac)
        }
        install_drop_rule(connection, 200, match, "MAC", mac, "*")
    
    # ═══════════════════════════════════════════════════════════════
    # RULE 3: BLOCK by DESTINATION PORT (Priority 150)
    # ═══════════════════════════════════════════════════════════════
    for port in BLOCKED_PORTS:
        match = {
            'dl_type': 0x0800,      # IPv4
            'nw_proto': 6,          # TCP
            'tp_dst': port          # Destination port
        }
        install_drop_rule(connection, 150, match, "PORT", "*", f"tcp:{port}")
    
    log.info("════════════════════════════════════════")
    log.info(f"[OK] All {2 + len(BLOCKED_IPS) + len(BLOCKED_MACS) + len(BLOCKED_PORTS)} rules installed")
    log.info("")

def _handle_PacketIn(event):
    """Handle packet-in events (for learning and debugging)"""
    packet = event.parsed
    
    if packet.find('ipv4'):
        src_ip = packet.find('ipv4').srcip
        dst_ip = packet.find('ipv4').dstip
        
        # Check if this is a blocked IP trying to send
        if str(src_ip) in BLOCKED_IPS:
            log.warning(f"[BLOCKED] Packet from blocked IP: {src_ip} → {dst_ip}")
            write_log("IP", str(src_ip), str(dst_ip), "DROPPED")

def launch():
    """Launch the firewall controller"""
    log.info("")
    log.info("╔════════════════════════════════════════╗")
    log.info("║  🔥 SDN FIREWALL CONTROLLER STARTED  ║")
    log.info("║  POX-Based Rule Engine                ║")
    log.info("╚════════════════════════════════════════╝")
    log.info("")
    
    # Register handlers
    core.openflow.addListenerByName("ConnectionUp", _handle_ConnectionUp)
    core.openflow.addListenerByName("PacketIn", _handle_PacketIn)
    
    log.info("✓ Listeners registered")
    log.info("✓ Waiting for switch connections...")
    log.info("")