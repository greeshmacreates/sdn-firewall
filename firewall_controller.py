"""
SDN-Based Firewall Controller using POX
Blocks traffic from/to specific IPs and MAC addresses.
Allows all other traffic using L2 learning switch logic.
"""

from pox.core import core
from pox.lib.util import dpidToStr
from pox.lib.addresses import IPAddr, EthAddr
import pox.openflow.libopenflow_01 as of
from pox.lib.packet import ethernet, ipv4, arp
from datetime import datetime

log = core.getLogger()

# ============================================================
# FIREWALL RULES - edit these to change blocking behavior
# ============================================================
BLOCKED_IPS  = ['10.0.0.3']          # h3 is blocked
BLOCKED_MACS = ['00:00:00:00:00:03'] # h3 MAC is blocked
# ============================================================

class FirewallController(object):

    def __init__(self, connection):
        self.connection = connection
        self.mac_to_port = {}
        connection.addListeners(self)
        log.info("Firewall Controller connected to switch: %s" % dpidToStr(connection.dpid))
        self._install_block_rules()

    def _install_block_rules(self):
        """Pre-install DROP rules for blocked IPs at high priority."""
        for ip in BLOCKED_IPS:
            msg = of.ofp_flow_mod()
            msg.priority = 100
            msg.match.dl_type = 0x0800   # IPv4
            msg.match.nw_src  = IPAddr(ip)
            # No actions = DROP
            self.connection.send(msg)
            log.info("[FIREWALL] DROP rule installed: src_ip=%s" % ip)
            self._log_blocked("RULE_INSTALL", ip, "N/A", "IP block rule installed at startup")

        for mac in BLOCKED_MACS:
            msg = of.ofp_flow_mod()
            msg.priority = 100
            msg.match.dl_src = EthAddr(mac)
            # No actions = DROP
            self.connection.send(msg)
            log.info("[FIREWALL] DROP rule installed: src_mac=%s" % mac)

    def _log_blocked(self, reason, src, dst, detail=""):
        """Write blocked packet info to log file."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        entry = "[%s] BLOCKED | reason=%s | src=%s | dst=%s | %s\n" % (
            timestamp, reason, src, dst, detail)
        with open("/home/%s/sdn-firewall/firewall.log" % __import__('os').getenv('USER'), "a") as f:
            f.write(entry)
        log.warning(entry.strip())

    def _handle_PacketIn(self, event):
        packet   = event.parsed
        in_port  = event.port
        dpid     = dpidToStr(self.connection.dpid)

        if not packet.parsed:
            return

        src_mac = str(packet.src)
        dst_mac = str(packet.dst)

        # Learn MAC -> port mapping
        self.mac_to_port[src_mac] = in_port

        # ── FIREWALL CHECK (MAC) ──────────────────────────────
        if src_mac in BLOCKED_MACS:
            self._log_blocked("MAC", src_mac, dst_mac)
            return  # drop silently

        # ── FIREWALL CHECK (IP) ───────────────────────────────
        ip_pkt = packet.find('ipv4')
        if ip_pkt:
            src_ip = str(ip_pkt.srcip)
            dst_ip = str(ip_pkt.dstip)
            if src_ip in BLOCKED_IPS:
                self._log_blocked("IP", src_ip, dst_ip)
                return  # drop silently

        # ── LEARNING SWITCH LOGIC ─────────────────────────────
        if dst_mac in self.mac_to_port:
            out_port = self.mac_to_port[dst_mac]

            # Install a flow rule so future packets skip controller
            msg = of.ofp_flow_mod()
            msg.priority  = 10
            msg.idle_timeout = 20
            msg.match.dl_dst = EthAddr(dst_mac)
            msg.match.dl_src = EthAddr(src_mac)
            msg.actions.append(of.ofp_action_output(port=out_port))
            self.connection.send(msg)
        else:
            out_port = of.OFPP_FLOOD

        # Send packet out
        msg = of.ofp_packet_out()
        msg.data    = event.ofp
        msg.in_port = in_port
        msg.actions.append(of.ofp_action_output(port=out_port))
        self.connection.send(msg)


class FirewallLauncher(object):
    def __init__(self):
        core.openflow.addListenerByName("ConnectionUp", self._handle_ConnectionUp)
        log.info("Firewall Controller waiting for switch connection...")

    def _handle_ConnectionUp(self, event):
        FirewallController(event.connection)


def launch():
    core.registerNew(FirewallLauncher)
