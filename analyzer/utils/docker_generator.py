import json
import os
import re
import subprocess

def detect_base_image(os_version): #TODO: Add support for other distros
    """Detects the correct base image and package manager."""

    os_version = os_version.lower()
    print(f"os_version:{os_version}")
    if "windows" in os_version:
        if "2019" in os_version:
            return "mcr.microsoft.com/windows/servercore:ltsc2019", "choco", "choco", "choco install -y"
        elif "2022" in os_version:
            return "mcr.microsoft.com/windows/servercore:ltsc2022", "choco", "choco", "choco install -y"
        else:
            return "mcr.microsoft.com/windows/servercore:latest", "choco", "choco", "choco install -y"

    if "kali" in os_version:
        return "kalilinux/kali-rolling:latest", "apt-get", "apt-get update", "apt-get install -y"
    elif "ubuntu" in os_version:
        return f"ubuntu:{os_version.replace('ubuntu ', '').strip()}", "apt-get", "apt-get update", "apt-get install -y"
    elif "debian" in os_version:
        return f"debian:{os_version.replace('debian ', '').strip()}", "apt-get", "apt-get update", "apt-get install -y"
    elif "arch" in os_version:
        return "archlinux:latest", "pacman", "pacman -Sy", "pacman -S --noconfirm"
    elif "centos" in os_version or "redhat" in os_version:
        return "centos:latest", "yum", "yum update -y", "yum install -y"
    elif "fedora" in os_version:
        return "fedora:latest", "dnf", "dnf update -y", "dnf install -y"
    elif "alpine" in os_version:
        return "alpine:latest", "apk", "apk update", "apk add --no-cache"
    else:
        return "ubuntu:20.04", "apt-get", "apt-get update", "apt-get install -y"

def get_container_ip(container_name):
    """Retrieve the IP address of a running Docker container."""
    try:
        result = subprocess.run(
            ["docker", "inspect", "-f", "{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}", container_name],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=True
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        print(f"Error retrieving container IP: {e.stderr}")
        return None

def spin_up_container_and_get_hostname(dockerfile_path, container_name):
    """Build and run the Docker container, then retrieve its hostname."""
    try:
        # Remove existing container with the same name, if any
        subprocess.run(
            ["docker", "rm", "-f", container_name],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        # Build the Docker image
        subprocess.run(
            ["docker", "build", "-t", container_name, "-f", dockerfile_path, "."],
            check=True
        )
        # Run the Docker container
        subprocess.run(
            ["docker", "run", "-d", "--name", container_name, container_name],
            check=True
        )
        # Retrieve the container's IP address
        container_ip = get_container_ip(container_name)
        if container_ip:
            # Assign the IP address to a hostname in /etc/hosts
            hostname = "docker-container.local"
            with open("/etc/hosts", "a") as hosts_file:
                hosts_file.write(f"{container_ip} {hostname}\n")
            print(f"Assigned hostname '{hostname}' to IP address {container_ip}")
            return hostname
        else:
            print("Error: Could not retrieve container IP address.")
            return None
    except subprocess.CalledProcessError as e:
        print(f"Error spinning up container: {e.stderr}")
        return None

def generate_dockerfile(json_file, output_directory="."):
    """Generates a Dockerfile for creating a system clone."""
    with open(json_file, "r") as f:
        config = json.load(f)

    os_info = config.get("os", {})
    os_version = os_info.get("os_version", "ubuntu 20.04")
    base_image, package_manager, update_cmd, install_cmd = detect_base_image(os_version)
    is_windows = "windows" in os_version.lower()

    dockerfile_content = [
        f"FROM {base_image}",
        'LABEL maintainer="SystemClone"',
        ""
    ]
    
    if not is_windows:
        dockerfile_content.extend([
            "# Set non-interactive mode",
            "ENV DEBIAN_FRONTEND=noninteractive",
            f"RUN {update_cmd}",
            ""
        ])
        # Ensure ssh, net-tools, and iptables are installed
        if package_manager == "apt-get":
            dockerfile_content.append("RUN apt-get update && apt-get install -y --no-install-recommends ssh net-tools iptables")
        elif package_manager in ("yum", "dnf"):
            dockerfile_content.append(f"RUN {package_manager} install -y ssh net-tools iptables")
        elif package_manager == "apk":
            dockerfile_content.append("RUN apk add --no-cache openssh net-tools iptables")
        dockerfile_content.append("")
    else:
        dockerfile_content.extend([
            "# Install Chocolatey",
            "RUN powershell -Command Set-ExecutionPolicy Bypass -Scope Process -Force; \"",
            "iex ((New-Object System.Net.WebClient).DownloadString('https://chocolatey.org/install.ps1'))",
            "RUN setx /M PATH \"%PATH%;C:\\ProgramData\\chocolatey\\bin\"",
            ""
        ])

    # Process software packages from the configuration.
    software = config.get("software", [])
    packages = []
    if isinstance(software, dict):
        if is_windows:
            packages = software.get("windows", [])
        else:
            packages = (software.get("debian", []) if "apt" in package_manager else
                        software.get("rhl", []) if package_manager in ("yum", "dnf") else
                        software.get("arch", []) if package_manager == "pacman" else
                        software.get("alpine", []) if package_manager == "apk" else [])
    elif isinstance(software, list):
        packages = software

    if packages:
        package_list = " ".join(packages)
        dockerfile_content.extend([
            "# Install required software packages",
            f"RUN {install_cmd} {package_list}",
            ""
        ])

    # Process user configuration from the config file.
    users_config = config.get("users", {}).get("users", "").split("\n")
    for user in users_config:
        parts = user.split(":")
        if len(parts) >= 7:
            username = parts[0]
            uid = int(parts[2]) if parts[2].isdigit() else 0
            home_dir = parts[5]
            shell = parts[6]
            if not username.startswith('_') and uid >= 1000 and shell not in ['/usr/sbin/nologin', '/bin/false'] and home_dir != '/nonexistent' and not username.startswith('nobody'):
                dockerfile_content.append(f"RUN useradd -m -d {home_dir} -s {shell} {username}")

    # Set environment variables excluding sensitive ones.
    env_vars = config.get("env_vars", {}).get("system_env", {})
    sensitive_keys = {"PASSWORD", "SECRET", "TOKEN", "API_KEY"}
    for key, value in env_vars.items():
        if not any(s in key.upper() for s in sensitive_keys):
            value = value.replace("\\", "/").rstrip("/")
            dockerfile_content.append(f'ENV {key}="{value}"')

    # Add a long-running process to keep the container alive
    dockerfile_content.extend([
        "# Keep the container running",
        'CMD ["tail", "-f", "/dev/null"]'
    ])

    # Write the Dockerfile to the output directory
    dockerfile_path = os.path.join(output_directory, "Dockerfile")
    with open(dockerfile_path, "w") as f:
        f.write("\n".join(dockerfile_content))

    print(f"Dockerfile generated successfully as {dockerfile_path}")

def apply_iptables_rules_on_host(firewall_script_path):
    """Apply iptables rules on the host system."""
    try:
        subprocess.run(["bash", firewall_script_path], check=True)
        print("Firewall rules applied successfully on the host.")
    except subprocess.CalledProcessError as e:
        print(f"Error applying firewall rules on the host: {e.stderr}")

def apply_iptables_rules_in_container(container_name, firewall_script_path):
    """Copy and apply iptables rules inside the container."""
    try:
        # Copy the firewall script to the container
        subprocess.run(
            ["docker", "cp", firewall_script_path, f"{container_name}:/firewall_setup.sh"],
            check=True
        )
        # Execute the firewall script inside the container
        subprocess.run(
            ["docker", "exec", container_name, "bash", "/firewall_setup.sh"],
            check=True
        )
        print("Firewall rules applied successfully in the container.")
    except subprocess.CalledProcessError as e:
        print(f"Error applying firewall rules in the container: {e.stderr}")

if __name__ == "__main__":
    generate_dockerfile("config_export/config.json")
