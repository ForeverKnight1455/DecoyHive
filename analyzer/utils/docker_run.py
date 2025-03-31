import subprocess
import os
import time
import signal
import sys

def container_exists(container_name):
    """Check if a container with the given name already exists."""
    try:
        result = subprocess.run(
            ["docker", "ps", "-a", "--filter", f"name={container_name}", "--format", "{{.Names}}"],
            stdout=subprocess.PIPE,
            text=True
        )
        return container_name in result.stdout.strip().split("\n")
    except subprocess.CalledProcessError as e:
        print(f"Error checking container existence: {e}")
        return False

def image_exists(image_name):
    """Check if a Docker image with the given name already exists."""
    try:
        result = subprocess.run(
            ["docker", "images", "--filter", f"reference={image_name}", "--format", "{{.Repository}}"],
            stdout=subprocess.PIPE,
            text=True
        )
        return image_name in result.stdout.strip().split("\n")
    except subprocess.CalledProcessError as e:
        print(f"Error checking image existence: {e}")
        return False

def get_container_identifier(container_name):
    """Return the container name or ID for use in configurations."""
    return container_name

def get_open_ports():
    """Use nmap to find open ports on the host system."""
    try:
        print("Scanning for open ports on the host system...")
        result = subprocess.run(
            ["nmap", "-p-", "--open", "127.0.0.1"],
            stdout=subprocess.PIPE,
            text=True,
            check=True
        )
        open_ports = []
        for line in result.stdout.splitlines():
            if "/tcp" in line and "open" in line:
                port = int(line.split("/")[0])
                open_ports.append(port)
        print(f"Open ports detected: {open_ports}")
        return open_ports
    except subprocess.CalledProcessError as e:
        print(f"Error scanning for open ports: {e}")
        return []

def setup_traffic_redirection(container_name, container_ip, open_ports):
    """Set up iptables rules on the host to redirect traffic to the container."""
    try:
        print(f"Setting up iptables rules to redirect traffic to container '{container_name}' (IP: {container_ip})...")

        for port in open_ports:
            subprocess.run([
                "iptables", "-t", "nat", "-A", "PREROUTING", "-p", "tcp", "--dport", str(port),
                "-j", "DNAT", "--to-destination", f"{container_ip}:{port}"
            ], check=True)

        # Ensure that the container's response is routed back to the host
        subprocess.run([
            "iptables", "-t", "nat", "-A", "POSTROUTING", "-s", container_ip, "-j", "MASQUERADE"
        ], check=True)

        print("Traffic redirection rules applied successfully on the host.")
    except subprocess.CalledProcessError as e:
        print(f"Error setting up iptables rules on the host: {e}")
        sys.exit(1)

def remove_iptables_in_container(container_name):
    """Remove iptables rules inside the Docker container."""
    try:
        # Create the iptables cleanup script
        cleanup_script = """#!/bin/bash
set -e
# Flush all iptables rules
iptables -F
iptables -t nat -F
iptables -X
iptables -t nat -X
"""
        script_path = "./output/iptables_cleanup.sh"
        with open(script_path, "w", newline="\n") as script_file:  # Ensure Unix-style line endings
            script_file.write(cleanup_script)

        # Copy the cleanup script into the container
        subprocess.run(
            ["docker", "cp", script_path, f"{container_name}:/iptables_cleanup.sh"],
            check=True
        )

        # Make the script executable inside the container
        subprocess.run(
            ["docker", "exec", container_name, "chmod", "+x", "/iptables_cleanup.sh"],
            check=True
        )

        # Execute the cleanup script inside the container
        subprocess.run(
            ["docker", "exec", container_name, "/bin/bash", "/iptables_cleanup.sh"],
            check=True
        )

        print("iptables rules removed successfully inside the container.")
    except subprocess.CalledProcessError as e:
        print(f"Error removing iptables rules inside the container: {e}")

def remove_traffic_redirection(container_name):
    """Remove iptables rules that redirect traffic to the container."""
    try:
        # Get the container's IP address
        result = subprocess.run(
            ["docker", "inspect", "-f", "{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}", container_name],
            stdout=subprocess.PIPE,
            text=True,
            check=True
        )
        container_ip = result.stdout.strip()
        if not container_ip:
            raise ValueError(f"Could not retrieve IP address for container '{container_name}'")

        print(f"Removing iptables rules for container '{container_name}' (IP: {container_ip})...")

        # Remove traffic redirection rules for specific ports (22, 80, 443)
        ports = [22, 80, 443]
        for port in ports:
            subprocess.run([
                "iptables", "-t", "nat", "-D", "PREROUTING", "-p", "tcp", "--dport", str(port),
                "-j", "DNAT", "--to-destination", f"{container_ip}:{port}"
            ], check=True)
        subprocess.run(["iptables", "-t", "nat", "-D", "POSTROUTING", "-s", container_ip, "-j", "MASQUERADE"], check=True)

        print("Traffic redirection rules removed successfully on the host.")
    except subprocess.CalledProcessError as e:
        print(f"Error removing iptables rules on the host: {e}")

def setup_iptables_in_container(container_name, open_ports):
    """Set up iptables rules inside the Docker container using a script."""
    try:
        # Create the iptables setup script
        iptables_script = """#!/bin/bash
set -e
# Flush existing iptables rules
iptables -F
iptables -t nat -F
iptables -X
iptables -t nat -X
"""
        for port in open_ports:
            iptables_script += f"iptables -t nat -A PREROUTING -p tcp --dport {port} -j REDIRECT --to-port {port}\n"

        iptables_script += "iptables -t nat -A POSTROUTING -j MASQUERADE\n"

        script_path = "./output/iptables_setup.sh"
        with open(script_path, "w", newline="\n") as script_file:  # Ensure Unix-style line endings
            script_file.write(iptables_script)

        # Copy the script into the container
        subprocess.run(
            ["docker", "cp", script_path, f"{container_name}:/iptables_setup.sh"],
            check=True
        )

        # Make the script executable inside the container
        subprocess.run(
            ["docker", "exec", container_name, "chmod", "+x", "/iptables_setup.sh"],
            check=True
        )

        # Execute the script inside the container
        subprocess.run(
            ["docker", "exec", container_name, "/bin/bash", "/iptables_setup.sh"],
            check=True
        )

        print(f"iptables rules configured successfully inside the container.")
    except subprocess.CalledProcessError as e:
        print(f"Error configuring iptables inside the container: {e}")
        sys.exit(1)

def setup_ssh_in_container(container_name):
    """Ensure the SSH server is running inside the container."""
    try:
        print(f"Setting up SSH server in container '{container_name}'...")

        # Install and start the SSH server inside the container
        subprocess.run(
            ["docker", "exec", container_name, "bash", "-c", "apt-get update && apt-get install -y openssh-server"],
            check=True
        )
        subprocess.run(
            ["docker", "exec", container_name, "bash", "-c", "mkdir -p /var/run/sshd"],
            check=True
        )
        subprocess.run(
            ["docker", "exec", container_name, "bash", "-c", "echo 'PermitRootLogin yes' >> /etc/ssh/sshd_config"],
            check=True
        )
        subprocess.run(
            ["docker", "exec", container_name, "bash", "-c", "service ssh start"],
            check=True
        )

        print("SSH server is running inside the container.")
    except subprocess.CalledProcessError as e:
        print(f"Error setting up SSH server in the container: {e}")
        sys.exit(1)

def build_and_run_docker():
    dockerfile_path = "./output/Dockerfile"
    image_name = "collected_data_image"
    container_name = "honeypot_container"

    if not os.path.exists(dockerfile_path):
        print("Error: Dockerfile not found! Ensure it is generated first.")
        sys.exit(1)

    try:
        # Check if the image already exists
        if not image_exists(image_name):
            print("Building Docker image...")
            subprocess.run([
                "docker", "build", "-t", image_name, "-f", dockerfile_path, "./output"
            ], check=True)
        else:
            print(f"Docker image '{image_name}' already exists. Reusing it.")

        # Check if the container already exists
        if not container_exists(container_name):
            print("Running Docker container with host networking...")
            subprocess.run([
                "docker", "run", "--name", container_name,
                "--network", "host",  # Use host networking
                "--cap-add=NET_ADMIN",
                "-d",
                image_name
            ], check=True)
            print(f"Container '{container_name}' is running.")
        else:
            print(f"Container '{container_name}' already exists. Reusing it.")

        # Use 127.0.0.1 as the container's IP address when using host networking
        container_ip = "127.0.0.1"

        # Get open ports on the host
        open_ports = get_open_ports()

        # Set up traffic redirection on the host
        setup_traffic_redirection(container_name, container_ip, open_ports)

        # Configure iptables inside the container
        setup_iptables_in_container(container_name, open_ports)

        # Return container name as the identifier
        return container_name
    except subprocess.CalledProcessError as e:
        print(f"Error: {e}")
        print("Ensure Docker is installed and running.")
        sys.exit(1)

def stop_container(container_name, image_name):
    try:
        print(f"Stopping container '{container_name}'...")
        subprocess.run(["docker", "stop", container_name], check=True)
        subprocess.run(["docker", "rm", container_name], check=True)
        print(f"Container '{container_name}' has been stopped and removed.")
    except subprocess.CalledProcessError as e:
        print(f"Error stopping/removing container: {e}")

    print(f"Deleting Docker image '{image_name}'...")
    try:
        subprocess.run(["docker", "rmi", image_name], check=True)
        print(f"Image '{image_name}' has been deleted.")
    except subprocess.CalledProcessError as e:
        print(f"Error deleting image: {e}")

def reset_host_iptables():
    """Reset iptables rules on the host to their default state."""
    try:
        print("Resetting iptables rules on the host to default state...")
        subprocess.run(["iptables", "-F"], check=True)
        subprocess.run(["iptables", "-t", "nat", "-F"], check=True)
        subprocess.run(["iptables", "-X"], check=True)
        subprocess.run(["iptables", "-t", "nat", "-X"], check=True)
        print("Host iptables rules reset successfully.")
    except subprocess.CalledProcessError as e:
        print(f"Error resetting iptables rules on the host: {e}")

def main():
    container_name = build_and_run_docker()

    def signal_handler(sig, frame):
        print("\nExiting script; cleaning up...")
        # Remove iptables rules inside the container
        remove_iptables_in_container(container_name)
        # Remove iptables rules on the host
        remove_traffic_redirection(container_name)
        # Reset iptables rules on the host to default
        reset_host_iptables()
        # Stop and remove the container
        stop_container(container_name, "collected_data_image")
        sys.exit(0)

    # Register signal handlers for graceful exit
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    print("Script running continuously. Press Ctrl+C to exit.")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        signal_handler(None, None)

if __name__ == "__main__":
    main()
