import subprocess
import re
import time
import os
import signal
import sys
import json
import netifaces
# Snort alert log file path
SNORT_LOG_PATH = "./snort_config/logs/alert"

# Regex pattern to extract source → destination mapping
LOG_REGEX = r"\b(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}):\d{1,5}\s*->\s*(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}):\d{1,5}\b"

active_rules = {}

# Function to fetch honeypot IP dynamically from Vagrant
def get_honeypot_ip():
    print("[INFO] Fetching honeypot IP from Vagrant...")

    try:
        result = subprocess.run(["vagrant", "ssh", "-c", "ip a | grep eth1 | grep inet"],
                                capture_output=True, text=True)
        print("[DEBUG] Vagrant SSH Output:\n", result.stdout)

        match = re.search(r"inet (\d+\.\d+\.\d+\.\d+)/", result.stdout)
        if match:
            honeypot_ip = match.group(1)
            print(f"[INFO] Honeypot IP detected: {honeypot_ip}")
            return honeypot_ip
        else:
            print("[ERROR] Failed to extract honeypot IP from Vagrant output.")
            return None
    except Exception as e:
        print(f"[ERROR] Exception while fetching honeypot IP: {e}")
        return None




def get_network_interfaces():
    return netifaces.interfaces()

# Function to get IP address of the chosen interface
def get_ip_address(interface):
    try:
        return netifaces.ifaddresses(interface)[netifaces.AF_INET][0]['addr']
    except (KeyError, IndexError):
        return None

def get_host_ip():
    # Ask the user for the network interface
    available_interfaces = get_network_interfaces()
    print("Available network interfaces:", ", ".join(available_interfaces))

    # read default_interface from config.json
    with open('./config.json', 'r') as f:
        config = json.load(f)
    interface = config.get('default_interface', None)


    if interface is None:
        while True:
            interface = input("Enter the network interface to monitor (e.g., eth0, wlan0, lo): ").strip()
            if interface in available_interfaces:
                ip_address = get_ip_address(interface)
                if ip_address:
                    break
                else:
                    print(f"Error: No IPv4 address found for {interface}. Try another one.")
            else:
                print("Invalid interface. Please select from the available ones.")
    else:
        ip_address  = get_ip_address(interface)

    print(f"Monitoring interface: {interface} (IP: {ip_address})")
    return ip_address

def redirect_traffic(attacker_ip, honeypot_ip, cooldown=60):
    print(f"[INFO] Temporarily dropping traffic from {attacker_ip}...")

    try:
        # Drop all packets from the attacker temporarily
        drop_command = ["sudo", "iptables", "-A", "INPUT", "-s", attacker_ip, "-j", "DROP"]
        subprocess.run(drop_command, check=True)

        print(f"[INFO] Traffic from {attacker_ip} is temporarily dropped. Waiting before redirection...")
        time.sleep(5)  # Wait before redirection

        # Remove the drop rule before redirection
        subprocess.run(["sudo", "iptables", "-D", "INPUT", "-s", attacker_ip, "-j", "DROP"], check=True)

        # Redirect all incoming traffic from the attacker to the honeypot
        subprocess.run(["sudo", "iptables", "-t", "nat", "-A", "PREROUTING", "-s", attacker_ip, "-j", "DNAT", "--to-destination", honeypot_ip], check=True)

        # Allow forwarding from attacker to honeypot
        subprocess.run(["sudo", "iptables", "-A", "FORWARD", "-s", attacker_ip, "-d", honeypot_ip, "-j", "ACCEPT"], check=True)

        # Enable SNAT (Source NAT) so honeypot's responses go back correctly
        subprocess.run(["sudo", "iptables", "-t", "nat", "-A", "POSTROUTING", "-s", honeypot_ip, "-j", "MASQUERADE"], check=True)


        print(f"[SUCCESS] Traffic from {attacker_ip} is now redirected to the honeypot.")

        # Store rules for cleanup
        #active_rules[attacker_ip] = [nat_command, forward_command]

        # Schedule removal after cooldown
        #time.sleep(cooldown)
        #remove_redirection(attacker_ip)

    except subprocess.CalledProcessError as e:
        print(f"[ERROR] iptables command failed: {e}")

# Function to parse Snort alerts and extract attacker IPs
def extract_attacker_ips(host_ip):
    attacker_ips = set()

    if not os.path.exists(SNORT_LOG_PATH):
        print(f"[WARNING] Snort log file {SNORT_LOG_PATH} not found!")
        return attacker_ips

    print(f"[INFO] Reading Snort alerts from {SNORT_LOG_PATH}...")

    try:
        with open(SNORT_LOG_PATH, "r") as f:
            lines = f.readlines()

        for line in lines:
            match = re.search(LOG_REGEX, line)
            if match:
                source_ip = match.group(1)
                dest_ip = match.group(2)

                # Ignore traffic from host machine
                if source_ip == host_ip:
                    print(f"[INFO] Ignoring traffic from host machine: {source_ip}")
                    continue

                print(f"[ALERT] Attacker Detected: {source_ip} → {dest_ip}")
                attacker_ips.add(source_ip)

        return attacker_ips

    except Exception as e:
        print(f"[ERROR] Exception while reading Snort logs: {e}")
        return set()


def rule_exists(rule):
    """Check if an iptables rule exists before deleting."""
    try:
        result = subprocess.run(["sudo", "iptables", "-C"] + rule, capture_output=True, text=True)
        return result.returncode == 0  # If return code is 0, rule exists
    except subprocess.CalledProcessError:
        return False

def remove_redirection(attacker_ip):
    if attacker_ip in active_rules:
        print(f"[INFO] Removing redirection for {attacker_ip}...")

        try:
            delete_nat_command = ["-t", "nat", "-D", "PREROUTING", "-s", attacker_ip, "-j", "DNAT", "--to-destination", honeypot_ip]
            delete_forward_command = ["-D", "FORWARD", "-s", attacker_ip, "-d", honeypot_ip, "-j", "ACCEPT"]
            delete_drop_command = ["-D", "INPUT", "-s", attacker_ip, "-j", "DROP"]
            # Check and remove NAT rule
            if rule_exists(delete_nat_command):
                subprocess.run(["sudo", "iptables"] + delete_nat_command, check=True)
                print(f"[INFO] NAT rule for {attacker_ip} removed.")

            # Check and remove FORWARD rule
            if rule_exists(delete_forward_command):
                subprocess.run(["sudo", "iptables"] + delete_forward_command, check=True)
                print(f"[INFO] FORWARD rule for {attacker_ip} removed.")

            # Check and remove DROP rule
            if rule_exists(delete_drop_command):
                subprocess.run(["sudo", "iptables"] + delete_drop_command, check=True)
                print(f"[INFO] DROP rule for {attacker_ip} removed.")

            # Remove from active tracking
            del active_rules[attacker_ip]

        except subprocess.CalledProcessError as e:
            print(f"[ERROR] Failed to remove iptables rule for {attacker_ip}: {e}")


def cleanup_and_exit(signal_received=None, frame=None):
    print("\n[INFO] Cleaning up iptables rules before exiting...")

    for attacker_ip in list(active_rules.keys()):
        remove_redirection(attacker_ip)

    # Flush all NAT, forwarding, and input rules
    try:
        subprocess.run(["sudo", "iptables", "-F", "FORWARD"], check=True)
        subprocess.run(["sudo", "iptables", "-t", "nat", "-F", "PREROUTING"], check=True)
        subprocess.run(["sudo", "iptables", "-t", "nat", "-F", "POSTROUTING"], check=True)
        subprocess.run(["sudo", "iptables", "-F", "INPUT"], check=True)  # Clear any lingering DROP rules

        print("[INFO] Flushed all forwarding, NAT, and input rules.")

    except subprocess.CalledProcessError as e:
        print(f"[ERROR] Failed to flush iptables rules: {e}")

    print("[INFO] Cleanup complete. Exiting.")
    sys.exit(0)


# Main loop
if __name__ == "__main__":
    print("[INFO] Starting traffic redirection script...")

    # Handle graceful exit
    signal.signal(signal.SIGINT, cleanup_and_exit)
    signal.signal(signal.SIGTERM, cleanup_and_exit)

    honeypot_ip = get_honeypot_ip()
    if not honeypot_ip:
        print("[FATAL] Could not retrieve honeypot IP. Exiting.")
        exit(1)

    host_ip = get_host_ip()
    if not host_ip:
        print("[FATAL] Could not determine host machine IP. Exiting.")
        exit(1)

    print(f"[INFO] Honeypot IP is {honeypot_ip}. Monitoring Snort alerts...")

    seen_ips = set()

    while True:
        attacker_ips = extract_attacker_ips(host_ip)

        for ip in attacker_ips:
            if ip not in seen_ips:
                seen_ips.add(ip)
                redirect_traffic(ip, honeypot_ip)

        time.sleep(1)  # Check logs every 10 seconds
