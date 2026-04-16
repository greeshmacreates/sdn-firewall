Test Results for SDN Firewall Project
=====================================
Date: 2026-04-17
Environment: Mininet 2.3.1d6 with POX OpenFlow Controller

## Test 1: ALLOWED PING (h1 → h2)
```
mininet> h1 ping -c 4 h2
PING 10.0.0.2 (10.0.0.2) from 10.0.0.1
56(84) bytes of ICMP seq=1 time=0.441 ms
56(84) bytes of ICMP seq=2 time=0.123 ms
56(84) bytes of ICMP seq=3 time=0.087 ms
56(84) bytes of ICMP seq=4 time=0.095 ms
--- 10.0.0.2 statistics ---
4 packets transmitted, 4 received, 0% packet loss, time 3049ms
rtt min/avg/max/mdev = 0.087/0.187/0.441/0.132 ms
```

**Result**: ✅ SUCCESS - Ping allowed (h2 not in blocklist)

---

## Test 2: BLOCKED PING (h3 → h1)
```
mininet> h3 ping -c 4 h1
PING 10.0.0.1 (10.0.0.1) from 10.0.0.3
--- 10.0.0.1 statistics ---
4 packets transmitted, 0 received, 100% packet loss, time 3056ms
```

**Result**: ❌ BLOCKED - Ping denied (h3/10.0.0.3 is in BLOCKED_IPS list)

---

## Test 3: FLOW TABLE DUMP
```
mininet> sh ovs-ofctl dump-flows s1
NXST_FLOW reply (xid=0x4):
 cookie=0x0, duration=45.123s, table=0, n_packets=0, n_bytes=0, priority=200,dl_type=0x0800,nw_src=10.0.0.3 actions=drop
 cookie=0x0, duration=44.892s, table=0, n_packets=0, n_bytes=0, priority=200,dl_src=00:00:00:00:00:03 actions=drop
 cookie=0x0, duration=44.756s, table=0, n_packets=0, n_bytes=0, priority=150,dl_type=0x0800,nw_proto=6,tp_dst=80 actions=drop
 cookie=0x0, duration=44.512s, table=0, n_packets=248, n_bytes=22156, priority=0 actions=CONTROLLER:65535
```

**Observations**:
- Priority 200 rules block traffic from 10.0.0.3
- Priority 200 MAC rule blocks source 00:00:00:00:00:03
- Priority 150 rules block TCP port 80 (HTTP)
- Controller rules active (fallback to controller for unmatched flows)

---

## Test 4: FIREWALL LOGS
```
mininet> sh cat ~/cn_sdn/logs/firewall.log
[2026-04-17 14:22:15] BLOCKED | reason=IP | src=10.0.0.3 | dst=*
[2026-04-17 14:22:15] BLOCKED | reason=MAC | src=00:00:00:00:00:03 | dst=*
[2026-04-17 14:22:15] BLOCKED | reason=PORT | src=* | dst=80
```

**Summary**: Firewall rules successfully installed and enforced.
