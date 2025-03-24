import subprocess
import re
import psutil
import logging
import sys
import os
import socket
from typing import List, Dict, Optional
import json

# Configure logging to log both to a file and the terminal
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("honeypot.log"),  # Log to file
        logging.StreamHandler()  # Log to terminal
    ]
)

def get_all_listening_ports() -> List[Dict]:
    """Get all listening ports using psutil."""
    listening_ports = []
    try:
        for conn in psutil.net_connections(kind='inet'):
            if conn.status == psutil.CONN_LISTEN:
                try:
                    process = psutil.Process(conn.pid)
                    listening_ports.append({
                        'port': conn.laddr.port,
                        'process_name': process.name(),
                        'process_id': conn.pid,
                        'process_cmdline': process.cmdline(),
                        'process_username': process.username(),
                        'protocol': 'tcp' if conn.type == socket.SOCK_STREAM else 'udp'
                    })
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    listening_ports.append({
                        'port': conn.laddr.port,
                        'process_name': 'Unknown',
                        'process_id': conn.pid,
                        'process_cmdline': [],
                        'process_username': 'Unknown',
                        'protocol': 'tcp' if conn.type == socket.SOCK_STREAM else 'udp'
                    })
    except Exception as e:
        logging.error(f"Error getting listening ports: {e}")
    return listening_ports

def get_service_banner(port: int, protocol: str = 'tcp') -> Optional[str]:
    """Attempt to get service banner from a port."""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(2)
            s.connect(('127.0.0.1', port))
            s.send(b'HEAD / HTTP/1.0\r\n\r\n')
            banner = s.recv(1024).decode('utf-8', errors='ignore')
            return banner.strip()
    except:
        return None

def run_nmap_scan(target: str = "localhost") -> str:
    """Runs an Nmap scan and streams the output live."""
    try:
        # First get all listening ports using psutil
        listening_ports = get_all_listening_ports()
        
        # Then run nmap for additional service information
        command = ["nmap", "-Pn", "-sV", "-p-", target]
        logging.info(f"Running Nmap scan: {' '.join(command)}")

        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        output_lines = []
        
        for line in iter(process.stdout.readline, ''):
            sys.stdout.write(line)
            sys.stdout.flush()
            logging.info(line.strip())
            output_lines.append(line.strip())

        process.stdout.close()
        process.wait()

        return "\n".join(output_lines)

    except FileNotFoundError:
        logging.error("Nmap is not installed. Please install it first.")
        return ""

def parse_nmap_output(nmap_output: str) -> List[Dict]:
    """Parses Nmap output and combines it with psutil information."""
    services = []
    listening_ports = get_all_listening_ports()
    
    # Create a map of ports to their psutil information
    port_info = {port['port']: port for port in listening_ports}
    
    for line in nmap_output.split("\n"):
        match = re.match(r"(\d+)/tcp\s+open\s+([\w-]+)", line)
        if match:
            port, service = match.groups()
            port = int(port)
            port_data = port_info.get(port, {})
            
            # Get service banner if available
            banner = get_service_banner(port)
            
            service_info = {
                "port": port,
                "service": service,
                "process_name": port_data.get('process_name', 'Unknown'),
                "process_id": port_data.get('process_id', None),
                "process_cmdline": port_data.get('process_cmdline', []),
                "process_username": port_data.get('process_username', 'Unknown'),
                "protocol": port_data.get('protocol', 'tcp'),
                "banner": banner
            }
            
            services.append(service_info)
            logging.info(f"Detected service: {service} on port {port}, process: {service_info['process_name']}")
    
    return services

def get_services_from_nmap(target: str = "localhost") -> List[Dict]:
    """Runs an Nmap scan and extracts service information."""
    nmap_output = run_nmap_scan(target)
    return parse_nmap_output(nmap_output)

# Example usage
if __name__ == "__main__":
    detected_services = get_services_from_nmap()
    for service in detected_services:
        print(f"Port: {service['port']}")
        print(f"Service: {service['service']}")
        print(f"Process: {service['process_name']}")
        print(f"Process ID: {service['process_id']}")
        print(f"Username: {service['process_username']}")
        print(f"Protocol: {service['protocol']}")
        if service['banner']:
            print(f"Banner: {service['banner']}")
        print("-" * 50)