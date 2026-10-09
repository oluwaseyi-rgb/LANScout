# LANScout

**A lightweight Python tool that discovers every device on your local Wi-Fi network.**

LANScout detects your subnet automatically, scans it, and prints a clean table of each connected device's IP address, MAC address, and hostname. It uses a fast ARP scan when `scapy` is available and falls back to a multithreaded ping sweep when it isn't, so it works almost anywhere.

---

## Features

- **Auto-detects your network**: finds your local IP and derives the `/24` subnet for you
- **Fast ARP scanning**: uses `scapy` for quick, reliable discovery
- **Automatic fallback**: switches to an ICMP ping sweep (100 concurrent threads) if `scapy` is missing or lacks permissions
- **Device details**: shows IP, MAC address, and hostname (via reverse DNS)
- **Self-identification**: marks your own machine with `<-- You`
- **Sorted output**: results are listed in numerical IP order
- **Cross-platform**: Windows, Linux, and macOS

---

## Requirements

- Python 3.7+
- `scapy` (optional, recommended for faster and more accurate results)
- Root/administrator privileges (required for ARP scanning)

```bash
pip install scapy
```

---

## Usage

**Linux / macOS**

```bash
sudo python3 lanscout.py
```

**Windows** (run the terminal as Administrator)

```powershell
python lanscout.py
```

---

## Example Output

```
============================================================
         Wi-Fi Network Scanner
============================================================
Your IP Address : 192.168.1.23
Scanning subnet : 192.168.1.0/24
------------------------------------------------------------
Attempting fast ARP scan (requires scapy + root)...

Found 4 device(s) on the network:

No.   IP Address         MAC Address          Hostname
----------------------------------------------------------------------
1     192.168.1.1        a4:2b:b0:11:22:33    router.local
2     192.168.1.15       3c:22:fb:44:55:66    Unknown
3     192.168.1.23       f0:18:98:77:88:99    my-laptop <-- You
4     192.168.1.40       b8:27:eb:aa:bb:cc    raspberrypi
------------------------------------------------------------
Scan complete.
```

---

## How It Works

1. **Find your IP**: opens a UDP socket to determine which local address is used for outbound traffic (no data is actually sent).
2. **Build the subnet**: takes the first three octets of your IP and scans `x.x.x.0/24`.
3. **ARP scan (preferred)**: broadcasts ARP requests with `scapy` and collects replies containing each device's IP and MAC.
4. **Ping sweep (fallback)**: pings all 254 host addresses in parallel, then reads each live host's MAC from the system ARP table.
5. **Resolve hostnames**: attempts a reverse DNS lookup for every device found, showing `Unknown` when none exists.

---

## Limitations

- Scans a `/24` subnet only (256 addresses), which covers most home and small-office networks
- The ping fallback can miss devices that block ICMP, and MAC lookup there depends on the ARP cache
- Hostnames depend on your network's DNS or mDNS setup, so many devices will show `Unknown`
- Without `scapy` or admin rights, results are less complete

---

## Troubleshooting

| Problem | Fix |
|---|---|
| "scapy not found or insufficient permissions" | Run `pip install scapy` and re-run with `sudo` / as Administrator |
| Windows ARP scan fails | Install [Npcap](https://npcap.com/) and run the terminal as Administrator |
| Fewer devices than expected | Some devices ignore pings or sleep; use the ARP scan and re-run once or twice |
| Wrong subnet detected | Check for active VPNs or multiple network adapters |

---

## Legal & Ethical Use

Only scan networks that you own or have explicit written permission to test. Unauthorized network scanning may violate laws and acceptable-use policies. The author is not responsible for misuse of this tool.

---

## Author

**Oladunni Oluwaseyi**
GitHub: [@oluwaseyi-rgb](https://github.com/oluwaseyi-rgb)
LinkedIn: [Oluwaseyi Oladunni](https://www.linkedin.com/in/oluwaseyi-oladunni-6a42b1407)

---

## License

Released under the MIT License. Feel free to use, modify, and share.
