import subprocess
import os
import time
import signal
import sys

def build_and_run_docker():
    dockerfile_path = "Dockerfile"
    image_name = "collected_data_image"
    container_name = "honeypot_container"

    if not os.path.exists(dockerfile_path):
        print("Error: Dockerfile not found! Ensure it is generated first.")
        sys.exit(1)

    try:
        print("Building Docker image...")
        subprocess.run(["docker", "build", "-t", image_name, "."], check=True)

        print("Running Docker container with port mappings...")
        subprocess.run([
            "docker", "run", "--name", container_name,
            "--cap-add=NET_ADMIN",
            "-d",
            "-p", "22:22",
            "-p", "80:80",
            "-p", "443:443",
            image_name
        ], check=True)
        print(f"Container '{container_name}' is running.")
        return container_name
    except subprocess.CalledProcessError as e:
        print(f"Error: {e}")
        print("Ensure Docker is installed and running.")
        sys.exit(1)

def get_container_ip(container_name):
    try:
        output = subprocess.check_output(
            ["docker", "inspect", "-f", "{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}", container_name]
        ).decode().strip()
        return output
    except subprocess.CalledProcessError as e:
        print(f"Error retrieving container IP: {e}")
        sys.exit(1)

def setup_iptables(container_ip):
    print("Setting up iptables redirection rules...")
    cmds = [
        # Redirect SSH traffic (port 22)
        ["iptables", "-t", "nat", "-A", "PREROUTING", "-p", "tcp", "--dport", "22", "-j", "DNAT", "--to-destination", f"{container_ip}:22"],
        ["iptables", "-t", "nat", "-A", "POSTROUTING", "-j", "MASQUERADE"],
        # Redirect HTTP traffic (port 80)
        ["iptables", "-t", "nat", "-A", "PREROUTING", "-p", "tcp", "--dport", "80", "-j", "DNAT", "--to-destination", f"{container_ip}:80"],
        ["iptables", "-t", "nat", "-A", "POSTROUTING", "-j", "MASQUERADE"],
        # Redirect HTTPS traffic (port 443)
        ["iptables", "-t", "nat", "-A", "PREROUTING", "-p", "tcp", "--dport", "443", "-j", "DNAT", "--to-destination", f"{container_ip}:443"],
        ["iptables", "-t", "nat", "-A", "POSTROUTING", "-j", "MASQUERADE"],
    ]
    for cmd in cmds:
        subprocess.run(cmd, check=True)
    print("iptables rules applied.")

def remove_iptables(container_ip):
    print("Removing iptables redirection rules...")
    cmds = [
        # Remove SSH redirection
        ["iptables", "-t", "nat", "-D", "PREROUTING", "-p", "tcp", "--dport", "22", "-j", "DNAT", "--to-destination", f"{container_ip}:22"],
        ["iptables", "-t", "nat", "-D", "POSTROUTING", "-j", "MASQUERADE"],
        # Remove HTTP redirection
        ["iptables", "-t", "nat", "-D", "PREROUTING", "-p", "tcp", "--dport", "80", "-j", "DNAT", "--to-destination", f"{container_ip}:80"],
        ["iptables", "-t", "nat", "-D", "POSTROUTING", "-j", "MASQUERADE"],
        # Remove HTTPS redirection
        ["iptables", "-t", "nat", "-D", "PREROUTING", "-p", "tcp", "--dport", "443", "-j", "DNAT", "--to-destination", f"{container_ip}:443"],
        ["iptables", "-t", "nat", "-D", "POSTROUTING", "-j", "MASQUERADE"],
    ]
    for cmd in cmds:
        try:
            subprocess.run(cmd, check=True)
        except subprocess.CalledProcessError:
            # If a rule was not found, continue
            pass
    print("iptables rules removed.")

def stop_container(container_name):
    try:
        print(f"Stopping container '{container_name}'...")
        subprocess.run(["docker", "stop", container_name], check=True)
        subprocess.run(["docker", "rm", container_name], check=True)
        print(f"Container '{container_name}' has been stopped and removed.")
    except subprocess.CalledProcessError as e:
        print(f"Error stopping/removing container: {e}")

def main():
    container_name = build_and_run_docker()
    container_ip = get_container_ip(container_name)
    setup_iptables(container_ip)

    def signal_handler(sig, frame):
        print("\nExiting script; cleaning up...")
        remove_iptables(container_ip)
        stop_container(container_name)
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
