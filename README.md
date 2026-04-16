# SDN-Based Firewall

## Overview
This project implements a Software Defined Networking (SDN) firewall using POX controller and Mininet.

## Features
- IP-based filtering
- MAC-based filtering
- Port-based filtering
- OpenFlow drop rules
- Logging of blocked traffic

## How Firewall Works
1. Switch sends packets to controller
2. Controller checks rules (IP/MAC/Port)
3. If match → DROP rule installed
4. Else → packet forwarded

## Execution Steps

### Start Controller
cd pox
python3 pox.py log.level --DEBUG ../controller/firewall.py forwarding.l2_learning

### Start Mininet
sudo mn --topo single,4 --controller remote --switch ovsk,protocols=OpenFlow10

## Test Cases

| Test | Command | Expected |
|------|--------|---------|
| Allowed | h1 ping h2 | Success |
| Blocked IP | h3 ping h1 | Fail |
| Blocked Port | curl 10.0.0.1 | Fail |