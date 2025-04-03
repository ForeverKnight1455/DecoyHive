import os
import subprocess
import netifaces
import json
# Function to get available network interfaces
def get_network_interfaces():
    return netifaces.interfaces()

# Function to get IP address of the chosen interface
def get_ip_address(interface):
    try:
        return netifaces.ifaddresses(interface)[netifaces.AF_INET][0]['addr']
    except (KeyError, IndexError):
        return None

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

# Configuration directory
CONFIG_DIR = "./snort_config"
SNORT_RULES_PATH = f"{CONFIG_DIR}/local.rules"
SNORT_CONFIG_PATH = f"{CONFIG_DIR}/snort.conf"
SNORT_CLASSIFICATION_PATH = f"{CONFIG_DIR}/classification.config"
SNORT_LOGS_PATH = f"{CONFIG_DIR}/logs"

# Create configuration directory
os.makedirs(CONFIG_DIR, exist_ok=True)
os.makedirs(SNORT_LOGS_PATH, exist_ok=True)

# Snort Rules for Suspicious Traffic Only
snort_rules = f"""
# Nmap Scan Detection (Require More Attempts)
alert tcp {ip_address} any -> any any (msg:"Nmap SYN Scan detected"; flags:S,12; threshold:type threshold, track by_src, count 10, seconds 20; sid:1000001;)
alert tcp {ip_address} any -> any any (msg:"Nmap FIN Scan detected"; flags:F; threshold:type threshold, track by_src, count 10, seconds 20; sid:1000002;)
alert tcp {ip_address} any -> any any (msg:"Nmap NULL Scan detected"; flags:0; threshold:type threshold, track by_src, count 10, seconds 20; sid:1000003;)
alert tcp {ip_address} any -> any any (msg:"Nmap Xmas Scan detected"; flags:FPU; threshold:type threshold, track by_src, count 10, seconds 20; sid:1000004;)
alert udp {ip_address} any -> any any (msg:"Nmap UDP Scan detected"; threshold:type threshold, track by_src, count 10, seconds 20; sid:1000005;)

# Port Scanning (Increase Count & Time Window)
alert tcp {ip_address} any -> any any (msg:"Port Scan Detected"; flags:S; threshold:type both, track by_src, count 15, seconds 10; sid:1000006;)

# DoS Attack Detection (Higher Threshold)
alert ip any any -> {ip_address} any (msg:"Possible DoS Attack on Host"; flow:to_client; threshold:type threshold, track by_dst, count 200, seconds 10; sid:1000008;)

# Spoofing Detection (No Change)
alert ip {ip_address} any -> {ip_address} any (msg:"Spoofing Attack Detected"; sid:1000009;)

# ICMP Attacks (Relax Thresholds)
alert icmp {ip_address} any -> any any (msg:"ICMP Fragmentation Attack"; fragbits:M+; sid:1000010;)
alert icmp {ip_address} any -> any any (msg:"ICMP with low TTL"; ttl:<5; sid:1000011;)
alert icmp {ip_address} any -> any any (msg:"ICMP Ping Flood Attack"; itype:8; threshold:type threshold, track by_src, count 50, seconds 10; sid:1000012;)

# SYN Flood Attack Detection (Higher Count)
alert tcp {ip_address} any -> any any (msg:"SYN Flood Attack Detected"; flags:S; threshold:type threshold, track by_src, count 200, seconds 10; sid:1000013;)

# SSH Brute Force Detection (Require More Attempts)
alert tcp any any -> {ip_address} 22 (msg:"Possible SSH Brute Force Attack"; flags:S; threshold:type threshold, track by_src, count 10, seconds 60; sid:2000001;)

# HTTP Brute Force Detection (Increase Time Window)
alert tcp any any -> {ip_address} any (msg:"Possible HTTP Brute Force Attack"; content:"401 Unauthorized"; http_uri; threshold:type threshold, track by_src, count 10, seconds 60; sid:2000002;)

# FTP Brute Force Detection (Relax Detection)
alert tcp any any -> {ip_address} 21 (msg:"Possible FTP Brute Force Attack"; content:"530 Login incorrect"; threshold:type threshold, track by_src, count 10, seconds 60; sid:2000003;)

# RDP Brute Force Detection (Higher Threshold)
alert tcp any any -> {ip_address} 3389 (msg:"Possible RDP Brute Force Attack"; flags:S; threshold:type threshold, track by_src, count 10, seconds 60; sid:2000004;)

# MySQL Brute Force Detection (Require More Attempts)
alert tcp any any -> {ip_address} 3306 (msg:"Possible MySQL Brute Force Attack"; content:"Access denied for user"; threshold:type threshold, track by_src, count 10, seconds 60; sid:2000005;)

"""

with open(SNORT_RULES_PATH, "w") as f:
    f.write(snort_rules)

# Snort Configuration File (Minimal required setup)
snort_conf = f"""
include classification.config
include local.rules
"""
with open(SNORT_CONFIG_PATH, "w") as f:
    f.write(snort_conf)

# Snort Classification Config
classification_config = """
config classification: attempted-recon,Attempted Information Leak,2
config classification: attempted-dos,Attempted Denial of Service,2
config classification: successful-dos,Denial of Service,1
config classification: attempted-user,Attempted User Privilege Gain,1
config classification: spoof-detected,Spoofing Attempt Detected,1
"""
with open(SNORT_CLASSIFICATION_PATH, "w") as f:
    f.write(classification_config)

# Docker Compose File for Snort
docker_compose_content = f"""
version: "3.8"

services:
  snort:
    image: frapsoft/snort
    container_name: snort
    restart: unless-stopped
    network_mode: "host"
    volumes:
      - {SNORT_RULES_PATH}:/etc/snort/local.rules
      - {SNORT_CONFIG_PATH}:/etc/snort/snort.conf
      - {SNORT_CLASSIFICATION_PATH}:/etc/snort/classification.config
      - {SNORT_LOGS_PATH}:/var/log/snort
    command: ["-A", "fast", "-q", "-c", "/etc/snort/snort.conf", "-i", "{interface}"]
"""

with open("docker-compose.yml", "w") as f:
    f.write(docker_compose_content)

# Start Docker container
print(f"Starting Snort IDS system on interface {interface} (IP: {ip_address})...")
subprocess.run(["docker", "compose", "up"], check=True)

print("Snort IDS is now running.")
