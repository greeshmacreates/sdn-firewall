# Firewall module for SDN controller
from pox.core import core
from pox.lib.addresses import IPAddr, EthAddr
import pox.openflow.libopenflow_01 as of
from datetime import datetime
import os

log = core.getLogger()

from controller.rules import BLOCKED_IPS, BLOCKED_MACS, BLOCKED_PORTS

LOG_FILE = os.path.expanduser("~/cn_sdn/logs/firewall.log")

def write_log(reason, src, dst):
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{ts}] BLOCKED | reason={reason} | src={src} | dst={dst}\n"

    with open(LOG_FILE, 'a') as f:
        f.write(line)

    log.warning(line.strip())

def _handle_ConnectionUp(event):
    log.info("Switch connected — installing firewall rules...")

    # BLOCK IP
    for ip in BLOCKED_IPS:
        msg = of.ofp_flow_mod()
        msg.priority = 200
        msg.match.dl_type = 0x0800
        msg.match.nw_src = IPAddr(ip)
        event.connection.send(msg)
        write_log("IP", ip, "*")

    # BLOCK MAC
    for mac in BLOCKED_MACS:
        msg = of.ofp_flow_mod()
        msg.priority = 200
        msg.match.dl_src = EthAddr(mac)
        event.connection.send(msg)
        write_log("MAC", mac, "*")

    # BLOCK PORT (TCP)
    for port in BLOCKED_PORTS:
        msg = of.ofp_flow_mod()
        msg.priority = 150
        msg.match.dl_type = 0x0800
        msg.match.nw_proto = 6
        msg.match.tp_dst = port
        event.connection.send(msg)
        write_log("PORT", "*", f"tcp:{port}")

def launch():
    core.openflow.addListenerByName("ConnectionUp", _handle_ConnectionUp)
    log.info("🔥 SDN Firewall Started")