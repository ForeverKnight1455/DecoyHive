import socket
import psutil
import subprocess
from typing import Dict, List, Tuple
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

def find_open_ports(host: str = "127.0.0.1", port_range: Tuple[int, int] = (1, 65535)) -> List[int]:
    """
    Scan a range of ports on a given host to find open ports.

    Args:
        host (str): The host to scan. Default is localhost ("127.0.0.1").
        port_range (Tuple[int, int]): The range of ports to scan. Default is (1, 65535).

    Returns:
        List[int]: A list of open ports.
    """
    open_ports = []
    start_port, end_port = port_range

    for port in range(start_port, end_port + 1):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.settimeout(0.1)  # Set a timeout for the connection attempt
                result = sock.connect_ex((host, port))
                if result == 0:  # Port is open if the result is 0
                    open_ports.append(port)
                    logging.info(f"Port {port} is open.")
        except Exception as e:
            logging.error(f"Error scanning port {port}: {e}")

    return open_ports

def get_services_for_ports(open_ports: List[int]) -> Dict[int, Dict[str, str]]:
    """
    Map open ports to their corresponding services and processes.

    Args:
        open_ports (List[int]): A list of open ports.

    Returns:
        Dict[int, Dict[str, str]]: A dictionary mapping ports to their service and process information.
    """
    port_service_map = {}

    for port in open_ports:
        try:
            # Get the service name for the port
            service_name = socket.getservbyport(port)
        except OSError:
            service_name = "unknown"

        # Find the process using the port
        process_info = None
        for conn in psutil.net_connections(kind='inet'):
            if conn.laddr.port == port and conn.status == psutil.CONN_LISTEN:
                try:
                    process = psutil.Process(conn.pid)
                    process_info = {
                        "pid": conn.pid,
                        "name": process.name(),
                        "cmdline": " ".join(process.cmdline()),
                    }
                    break
                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                    continue

        port_service_map[port] = {
            "service": service_name,
            "process": process_info if process_info else "unknown",
        }

    return port_service_map

def get_service_version(service_name: str) -> str:
    """
    Get the version of a running service.

    Args:
        service_name (str): The name of the service.

    Returns:
        str: The version of the service, or "unknown" if not found.
    """
    try:
        if service_name == "ssh":
            result = subprocess.run(["ssh", "-V"], capture_output=True, text=True)
            return result.stderr.strip()
        elif service_name == "http" or service_name == "https":
            result = subprocess.run(["nginx", "-v"], capture_output=True, text=True)
            return result.stderr.strip()
        elif service_name == "postgresql":
            result = subprocess.run(["psql", "--version"], capture_output=True, text=True)
            return result.stdout.strip()
        elif service_name == "mysql":
            result = subprocess.run(["mysql", "--version"], capture_output=True, text=True)
            return result.stdout.strip()
        else:
            return "unknown"
    except Exception as e:
        logging.error(f"Error getting version for {service_name}: {e}")
        return "unknown"

def scan_ports_and_services(host: str = "127.0.0.1", port_range: Tuple[int, int] = (1, 65535)) -> Dict[int, Dict[str, str]]:
    """
    Scan for open ports and map them to their corresponding services and processes.

    Args:
        host (str): The host to scan. Default is localhost ("127.0.0.1").
        port_range (Tuple[int, int]): The range of ports to scan. Default is (1, 65535).

    Returns:
        Dict[int, Dict[str, str]]: A dictionary mapping ports to their service and process information.
    """
    logging.info(f"Scanning ports on {host}...")
    open_ports = find_open_ports(host, port_range)
    logging.info(f"Found {len(open_ports)} open ports.")

    if not open_ports:
        return {}

    logging.info("Mapping ports to services and processes...")
    port_service_map = get_services_for_ports(open_ports)

    # Get versions for each service
    for port, info in port_service_map.items():
        service_name = info["service"]
        info["version"] = get_service_version(service_name)

    return port_service_map

def generate_dockerfile(port_service_map: Dict[int, Dict[str, str]], output_file: str = "Dockerfile"):
    """
    Generate a Dockerfile based on the detected services and their versions.

    Args:
        port_service_map (Dict[int, Dict[str, str]]): A dictionary mapping ports to their service and process information.
        output_file (str): The name of the output Dockerfile. Default is "Dockerfile".
    """
    with open(output_file, "w") as dockerfile:
        dockerfile.write("# Generated Dockerfile\n")
        dockerfile.write("FROM ubuntu:latest\n\n")

        # Install services
        for port, info in port_service_map.items():
            service_name = info["service"]
            version = info["version"]

            if service_name == "ssh":
                dockerfile.write("# Install SSH\n")
                dockerfile.write("RUN apt-get update && apt-get install -y openssh-server\n")
                dockerfile.write(f'RUN echo "Version: {version}" >> /service_versions.txt\n\n')
            elif service_name == "http" or service_name == "https":
                dockerfile.write("# Install Nginx\n")
                dockerfile.write("RUN apt-get update && apt-get install -y nginx\n")
                dockerfile.write(f'RUN echo "Version: {version}" >> /service_versions.txt\n\n')
            elif service_name == "postgresql":
                dockerfile.write("# Install PostgreSQL\n")
                dockerfile.write("RUN apt-get update && apt-get install -y postgresql\n")
                dockerfile.write(f'RUN echo "Version: {version}" >> /service_versions.txt\n\n')
            elif service_name == "mysql":
                dockerfile.write("# Install MySQL\n")
                dockerfile.write("RUN apt-get update && apt-get install -y mysql-server\n")
                dockerfile.write(f'RUN echo "Version: {version}" >> /service_versions.txt\n\n')
            else:
                dockerfile.write(f"# Service {service_name} is not supported in this Dockerfile\n\n")

        # Expose ports
        dockerfile.write("# Expose ports\n")
        for port in port_service_map.keys():
            dockerfile.write(f"EXPOSE {port}\n")

        # Add a command to keep the container running
        dockerfile.write("\nCMD [\"tail\", \"-f\", \"/dev/null\"]\n")

    logging.info(f"Dockerfile generated at {output_file}")

if __name__ == "__main__":
    # Example usage
    results = scan_ports_and_services()
    for port, info in results.items():
        print(f"Port: {port}")
        print(f"  Service: {info['service']}")
        print(f"  Version: {info['version']}")
        print(f"  Process: {info['process']}")
        print()

    # Generate Dockerfile
    generate_dockerfile(results)
