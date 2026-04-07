"""
SDN Firewall Topology:
  h1 (10.0.0.1) - ALLOWED
  h2 (10.0.0.2) - ALLOWED
  h3 (10.0.0.3) - BLOCKED by firewall
  All connected to s1, controlled by POX remote controller
"""

from mininet.net import Mininet
from mininet.node import RemoteController, OVSSwitch
from mininet.cli import CLI
from mininet.log import setLogLevel, info

def create_topology():
    net = Mininet(controller=RemoteController, switch=OVSSwitch)

    info("*** Adding controller\n")
    c0 = net.addController('c0', ip='127.0.0.1', port=6633)

    info("*** Adding switch\n")
    s1 = net.addSwitch('s1', protocols='OpenFlow10')

    info("*** Adding hosts\n")
    h1 = net.addHost('h1', ip='10.0.0.1/24', mac='00:00:00:00:00:01')
    h2 = net.addHost('h2', ip='10.0.0.2/24', mac='00:00:00:00:00:02')
    h3 = net.addHost('h3', ip='10.0.0.3/24', mac='00:00:00:00:00:03')  # BLOCKED

    info("*** Adding links\n")
    net.addLink(h1, s1)
    net.addLink(h2, s1)
    net.addLink(h3, s1)

    info("*** Starting network\n")
    net.start()

    info("\n*** TOPOLOGY READY ***\n")
    info("h1=10.0.0.1 (ALLOWED)\n")
    info("h2=10.0.0.2 (ALLOWED)\n")
    info("h3=10.0.0.3 (BLOCKED by firewall)\n\n")

    CLI(net)
    net.stop()

if __name__ == '__main__':
    setLogLevel('info')
    create_topology()
