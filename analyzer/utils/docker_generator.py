import json
import os
import re

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

def generate_dockerfile(json_file,output_directory = "."):
    """Generates a Dockerfile for creating a system clone and creates a firewall_setup.sh if firewall rules exist."""
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
        # Ensure iptables and net-tools are installed so that firewall rules work at runtime.
        if package_manager == "apt-get":
            dockerfile_content.append("RUN apt-get update && apt-get install -y --no-install-recommends iptables net-tools ssh netcat-traditional")
        elif package_manager in ("yum", "dnf"):
            dockerfile_content.append(f"RUN {package_manager} install -y iptables net-tools ssh netcat-traditional")
        elif package_manager == "apk":
            dockerfile_content.append("RUN apk add --no-cache iptables net-tools ssh netcat-traditional")
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

    # Process network configuration for honeypot traffic redirection.
    network_config = config.get("network", {})
    honeypot_port = network_config.get("honeypot_port", 8080)  # Default honeypot port.
    if network_config and not is_windows:
        dockerfile_content.append("\n# Configure networking")
        if "ip_address" in network_config:
            dockerfile_content.append(f'RUN echo "IP Address: {network_config["ip_address"]}"')

    # Generate iptables rules for traffic redirection to the honeypot container.
    firewall_rules = network_config.get("firewall_rules", "").split("\n")
    if firewall_rules and not is_windows:
        firewall_script_lines = ["#!/bin/bash", "set -e"]
        for rule in firewall_rules:
            rule = rule.strip()
            if rule:
                # Look for a rule matching "Chain <chain> (policy <policy>)"
                match = re.match(r"Chain\s+(\S+)\s*\(policy\s+(\S+)\)", rule)
                if match:
                    chain, policy = match.groups()
                    firewall_script_lines.append(f"iptables -P {chain} {policy}")
                else:
                    firewall_script_lines.append(f"# WARNING: Unrecognized firewall rule format skipped: {rule}")

        # Add iptables rules to redirect traffic to the honeypot container.
        firewall_script_lines.extend([
            "# Redirect traffic to the honeypot container",
            f"iptables -t nat -A PREROUTING -p tcp --dport 80 -j REDIRECT --to-port {honeypot_port}",
            f"iptables -t nat -A PREROUTING -p tcp --dport 443 -j REDIRECT --to-port {honeypot_port}",
        ])

        # Allow open ports specified in the ports section of config.json.
        ports_config = config.get("ports", [])
        known_ports = {22, 80, 443, 8080, 3306, 5432}  # Example list of known port numbers
        if ports_config:
            firewall_script_lines.append("# Allow open ports specified in the configuration")
            for port_entry in ports_config:
                port = port_entry.get("port")
                if isinstance(port, int) and 1 <= port <= 65535:
                    if port in known_ports:
                        firewall_script_lines.append(f"iptables -A INPUT -p tcp --dport {port} -j ACCEPT")
                    else:
                        firewall_script_lines.append(f"# Port {port} is not in the known list, mapping to netcat listener")
                        firewall_script_lines.append(f"iptables -A INPUT -p tcp --dport {port} -j ACCEPT")
                        firewall_script_lines.append(
                            f"(while true; do echo 'Listening on port {port}' | nc -lk -p {port}; done) &"
                        )
                else:
                    firewall_script_lines.append(f"# WARNING: Invalid port skipped: {port}")

        # After firewall setup, execute the CMD provided to the container.
        firewall_script_lines.append('exec "$@"')
        # Write the firewall_setup.sh file to the build context.
        with open(f"{output_directory}/firewall_setup.sh", "w") as fw:
            fw.write("\n".join(firewall_script_lines))
        # In the Dockerfile, copy the script and set it as the ENTRYPOINT.
        dockerfile_content.append(f"COPY firewall_setup.sh /firewall_setup.sh")
        dockerfile_content.append("RUN chmod +x /firewall_setup.sh")
        dockerfile_content.append("ENTRYPOINT [\"/firewall_setup.sh\"]")
        # Specify the default command.
        dockerfile_content.append('CMD ["tail", "-f", "/dev/null"]')
    else:
        # If no firewall rules, simply set the default command.
        dockerfile_content.append('CMD ["tail", "-f", "/dev/null"]')

    with open(f"{output_directory}/Dockerfile", "w") as f:
        f.write("\n".join(dockerfile_content))

    print(f"Dockerfile generated successfully as {output_directory}/Dockerfile")
    if firewall_rules and not is_windows:
        print("firewall_setup.sh generated successfully.")

if __name__ == "__main__":
    generate_dockerfile("config_export/config.json")
