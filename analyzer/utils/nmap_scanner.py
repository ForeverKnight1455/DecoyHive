import subprocess
import re
import psutil
import logging
import sys

# Configure logging to log both to a file and the terminal
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("honeypot.log"),  # Log to file
        logging.StreamHandler()  # Log to terminal
    ]
)

def run_nmap_scan(target="127.0.0.1"):
    """Runs an Nmap scan and streams the output live."""

    # Enforce root privileges
    if os.getuid() != 0:
        print("This script must be run as root. Please Enter your sudo password")


    try:
        command = ["sudo", "nmap", "-Pn", "-sV", "-p-", "-vv", target]  # Nmap scan with service detection
        logging.info(f"Running Nmap scan: {' '.join(command)}")

        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)

        # Stream output in real-time
        output_lines = []
        for line in iter(process.stdout.readline, ''):
            sys.stdout.write(line)  # Print to terminal in real-time
            sys.stdout.flush()
            logging.info(line.strip())  # Log to file
            output_lines.append(line.strip())

        process.stdout.close()
        process.wait()

        return "\n".join(output_lines)

    except FileNotFoundError:
        logging.error("Nmap is not installed. Please install it first.")
        return ""

def parse_nmap_output(nmap_output):
    """Parses Nmap output and extracts open ports with their services."""
    services = []
    for line in nmap_output.split("\n"):
        match = re.match(r"(\d+)/tcp\s+open\s+([\w-]+)", line)
        if match:
            port, service = match.groups()
            process_name = find_process_by_port(int(port))
            services.append({
                "port": int(port),
                "service": service,
                "process_name": process_name
            })
            logging.info(f"Detected service: {service} on port {port}, process: {process_name}")
    return services

def find_process_by_port(port):
    """Finds the process name listening on a given port using psutil."""
    for conn in psutil.net_connections(kind='inet'):
        if conn.laddr.port == port and conn.status == psutil.CONN_LISTEN:
            try:
                return psutil.Process(conn.pid).name()
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                return "Unknown"
    return "None"

def get_services_from_nmap():
    """Runs an Nmap scan and extracts service information."""
    nmap_output = run_nmap_scan()
    return parse_nmap_output(nmap_output)

# Example usage
if __name__ == "__main__":
    detected_services = get_services_from_nmap()
    for service in detected_services:
        print(f"Port: {service['port']}, Service: {service['service']}, Process: {service['process_name']}")
