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
import sys

log = core.getLogger()

from rules import BLOCKED_IPS, BLOCKED_MACS, BLOCKED_PORTS

# ═══════════════════════════════════════════════════════════════════
# LOGGING CONFIGURATION
# ═══════════════════════════════════════════════════════════════════

# Try multiple log file paths
LOG_PATHS = [
    os.path.expanduser("~/cn_sdn/logs/firewall.log"),
    "/mnt/c/Users/Greeshma/cn_sdn/logs/firewall.log",
    "/root/cn_sdn/logs/firewall.log",
    "./firewall.log"
]

LOG_FILE = None

def setup_log_file():
    """Find and setup the log file"""
    global LOG_FILE
    
    for path in LOG_PATHS:
        try:
            # Create directory if needed
            log_dir = os.path.dirname(path)
            if log_dir and not os.path.exists(log_dir):
                os.makedirs(log_dir, exist_ok=True)
            
            # Test if we can write to this path
            with open(path, 'a') as f:
                f.write("")
            
            LOG_FILE = path
            log.info(f"✓ Log file configured: {LOG_FILE}")
            return path
        except Exception as e:
            continue
    
    # Fallback to current directory
    LOG_FILE = "./firewall.log"
    log.warning(f"Using fallback log path: {LOG_FILE}")
    return LOG_FILE

def write_log(reason, src, dst, action="BLOCKED", packet_info=""):
    """
    Log blocked packet information with timestamp
    
    Args:
        reason: Type of rule (IP, MAC, PORT)
        src: Source (IP or MAC)
        dst: Destination (IP, port, or *)
        action: Log action type (BLOCKED, DROPPED, ALLOWED)
        packet_info: Additional packet details
    """
    if not LOG_FILE:
        setup_log_file()
    
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
    
    # Format: [timestamp] ACTION | rule=TYPE | src=SOURCE | dst=DESTINATION | extra_info
    line = f"[{ts}] {action:8} | rule={reason:6} | src={src:15} | dst={dst:15}"
    
    if packet_info:
        line += f" | info={packet_info}"
    
    line += "\n"
    
    try:
        with open(LOG_FILE, 'a') as f:
            f.write(line)
        log.warning(line.strip())
    except Exception as e:
        log.error(f"✗ Failed to write log: {e}")
        sys.stderr.write(f"[LOG ERROR] {e}\n")

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
    """
    Handle packet-in events for monitoring blocked traffic
    
    This function is called when a packet reaches the controller:
    - Logs packets from blocked hosts
    - Logs packets destined to blocked ports
    - Provides audit trail of blocked attempted communications
    """
    packet = event.parsed
    
    try:
        # Check Ethernet header
        src_mac = str(packet.src) if hasattr(packet, 'src') else "unknown"
        dst_mac = str(packet.dst) if hasattr(packet, 'dst') else "unknown"
        
        # Check if blocked by MAC
        if src_mac in BLOCKED_MACS:
            log.warning(f"[PACKET BLOCKED] MAC {src_mac} attempted packet")
            write_log("MAC", src_mac, dst_mac, "DROPPED", f"Layer2_blocked")
        
        # Check IP layer
        if packet.find('ipv4'):
            ipv4 = packet.find('ipv4')
            src_ip = str(ipv4.srcip)
            dst_ip = str(ipv4.dstip)
            protocol = ipv4.protocol
            
            # Log blocked source IP
            if src_ip in BLOCKED_IPS:
                log.warning(f"[PACKET BLOCKED] IP {src_ip} → {dst_ip} (protocol: {protocol})")
                write_log("IP", src_ip, dst_ip, "DROPPED", f"Protocol_{protocol}")
            
            # Check TCP layer for blocked ports
            if protocol == 6:  # TCP
                tcp = packet.find('tcp')
                if tcp:
                    dst_port = tcp.dstport
                    if dst_port in BLOCKED_PORTS:
                        log.warning(f"[PACKET BLOCKED] Port {dst_port} access from {src_ip}")
                        write_log("PORT", src_ip, f"tcp:{dst_port}", "DROPPED", f"Port_blocked")
    
    except Exception as e:
        log.error(f"Error in packet-in handler: {e}")

def launch():
    """Launch the firewall controller"""
    # Setup logging first
    setup_log_file()
    
    log.info("")
    log.info("╔════════════════════════════════════════╗")
    log.info("║  🔥 SDN FIREWALL CONTROLLER STARTED  ║")
    log.info("║  POX-Based Rule Engine                ║")
    log.info("╚════════════════════════════════════════╝")
    log.info("")
    
    # Write startup message to log
    write_log("INIT", "controller", "system", "STARTED", "Firewall_controller_initialized")
    
    # Log configuration
    log.info(f"Blocked IPs: {BLOCKED_IPS}")
    log.info(f"Blocked MACs: {BLOCKED_MACS}")
    log.info(f"Blocked Ports: {BLOCKED_PORTS}")
    log.info("")
    
    # Register handlers
    core.openflow.addListenerByName("ConnectionUp", _handle_ConnectionUp)
    core.openflow.addListenerByName("PacketIn", _handle_PacketIn)
    
    log.info("✓ Listeners registered")
    log.info("✓ Waiting for switch connections...")
    log.info("")