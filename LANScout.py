"""
Wi-Fi Network Scanner
Scans your local network and lists all device IP addresses.

Requirements:
    pip install scapy
    Run with sudo/admin privileges for best results.

Usage:
    sudo python3 LANScout.py
"""

import subprocess
import socket
import ipaddress
import platform
import sys
import re
from concurrent.futures import ThreadPoolExecutor, as_completed


def get_local_ip():
    """Get the local machine's IP address."""
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("8.8.8.8", 80))
        return s.getsockname()[0]
    except Exception:
        return "127.0.0.1"
    finally:
        s.close()


def get_subnet(local_ip):
    """Derive the /24 subnet from the local IP."""
    parts = local_ip.split(".")
    return f"{parts[0]}.{parts[1]}.{parts[2]}.0/24"


def ping_host(ip):
    """Ping a single IP. Returns IP if alive, else None."""
    os_name = platform.system()
    if os_name == "Windows":
        cmd = ["ping", "-n", "1", "-w", "500", str(ip)]
    else:
        cmd = ["ping", "-c", "1", "-W", "1", str(ip)]

    try:
        result = subprocess.run(
            cmd,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            timeout=2
        )
        if result.returncode == 0:
            return str(ip)
    except (subprocess.TimeoutExpired, Exception):
        pass
    return None


def get_hostname(ip):
    """Try to resolve a hostname for the given IP."""
    try:
        return socket.gethostbyaddr(ip)[0]
    except socket.herror:
        return "Unknown"


def get_mac_from_arp(ip):
    """
    Try to get the MAC address from the ARP table.
    Works after a ping has been sent to the host.
    """
    os_name = platform.system()
    try:
        if os_name == "Windows":
            output = subprocess.check_output(["arp", "-a", ip], timeout=3).decode()
            match = re.search(r"([0-9A-Fa-f]{2}[:-]){5}[0-9A-Fa-f]{2}", output)
        else:
            output = subprocess.check_output(["arp", "-n", ip], timeout=3).decode()
            match = re.search(r"([0-9a-fA-F]{2}[:\-]){5}([0-9a-fA-F]{2})", output)
        if match:
            return match.group(0)
    except Exception:
        pass
    return "N/A"


def try_scapy_scan(subnet):
    """
    Use scapy for ARP scanning if available — faster and more reliable.
    Returns list of dicts with ip and mac, or None if scapy not installed.
    """
    try:
        from scapy.all import ARP, Ether, srp  # type: ignore
        packet = Ether(dst="ff:ff:ff:ff:ff:ff") / ARP(pdst=subnet)
        answered, _ = srp(packet, timeout=2, verbose=False)
        results = []
        for _, rcv in answered:
            results.append({"ip": rcv.psrc, "mac": rcv.hwsrc})
        return results
    except ImportError:
        return None
    except Exception:
        return None


def scan_with_ping(subnet):
    """Fallback: scan using ICMP ping + ARP table lookup."""
    network = ipaddress.IPv4Network(subnet, strict=False)
    hosts = list(network.hosts())

    print(f"Pinging {len(hosts)} addresses (this may take ~30 seconds)...\n")

    alive_ips = []
    with ThreadPoolExecutor(max_workers=100) as executor:
        futures = {executor.submit(ping_host, ip): ip for ip in hosts}
        for future in as_completed(futures):
            result = future.result()
            if result:
                alive_ips.append(result)

    return sorted(alive_ips, key=lambda ip: list(map(int, ip.split("."))))


def print_banner():
    print("=" * 60)
    print("         Wi-Fi Network Scanner")
    print("=" * 60)


def main():
    print_banner()

    local_ip = get_local_ip()
    subnet = get_subnet(local_ip)

    print(f"Your IP Address : {local_ip}")
    print(f"Scanning subnet : {subnet}")
    print("-" * 60)

    # --- Try scapy first (fast ARP scan) ---
    print("Attempting fast ARP scan (requires scapy + root)...")
    scapy_results = try_scapy_scan(subnet)

    if scapy_results is not None:
        print(f"\nFound {len(scapy_results)} device(s) on the network:\n")
        print(f"{'No.':<5} {'IP Address':<18} {'MAC Address':<20} {'Hostname'}")
        print("-" * 70)
        for i, device in enumerate(
            sorted(scapy_results, key=lambda d: list(map(int, d["ip"].split(".")))), 1
        ):
            hostname = get_hostname(device["ip"])
            tag = " <-- You" if device["ip"] == local_ip else ""
            print(f"{i:<5} {device['ip']:<18} {device['mac']:<20} {hostname}{tag}")

    else:
        # --- Fallback: ping sweep ---
        print("scapy not found or insufficient permissions — using ping sweep.\n")
        alive_ips = scan_with_ping(subnet)

        print(f"\nFound {len(alive_ips)} device(s) on the network:\n")
        print(f"{'No.':<5} {'IP Address':<18} {'MAC Address':<20} {'Hostname'}")
        print("-" * 70)
        for i, ip in enumerate(alive_ips, 1):
            hostname = get_hostname(ip)
            mac = get_mac_from_arp(ip)
            tag = " <-- You" if ip == local_ip else ""
            print(f"{i:<5} {ip:<18} {mac:<20} {hostname}{tag}")

    print("-" * 60)
    print("Scan complete.")
    print()
    print("TIP: For faster, more accurate results:")
    print("  pip install scapy")
    print("  sudo python3 wifi_scanner.py")


if __name__ == "__main__":
    main()
