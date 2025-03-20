import json
import os
import re

def detect_base_image(os_version):
    """Detects the correct base image and package manager."""
    os_version = os_version.lower()

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
            dockerfile_content.append("RUN apt-get install -y iptables net-tools")
        elif package_manager in ("yum", "dnf"):
            dockerfile_content.append(f"RUN {package_manager} install -y iptables net-tools")
        elif package_manager == "apk":
            dockerfile_content.append("RUN apk add --no-cache iptables net-tools")
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
            if not username.startswith('_') and uid >= 1000 and shell not in ['/usr/sbin/nologin', '/bin/false'] and home_dir != '/nonexistent':
                dockerfile_content.append(f"RUN useradd -m -d {home_dir} -s {shell} {username}")

    # Set environment variables excluding sensitive ones.
    env_vars = config.get("env_vars", {}).get("system_env", {})
    sensitive_keys = {"PASSWORD", "SECRET", "TOKEN", "API_KEY"}
    for key, value in env_vars.items():
        if not any(s in key.upper() for s in sensitive_keys):
            value = value.replace("\\", "/").rstrip("/")
            dockerfile_content.append(f'ENV {key}="{value}"')

    # Configure networking (this example just echoes the IP; adjust as needed).
    network_config = config.get("network", {})
    if network_config and not is_windows:
        dockerfile_content.append("\n# Configure networking")
        if "ip_address" in network_config:
            dockerfile_content.append(f'RUN echo "IP Address: {network_config["ip_address"]}"')

    # Instead of running iptables commands at build time, generate a startup script.
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
        # After firewall setup, execute the CMD provided to the container.
        firewall_script_lines.append('exec "$@"')
        # Write the firewall_setup.sh file to the build context.
        with open(f"{output_directory}/firewall_setup.sh", "w") as fw:
            fw.write("\n".join(firewall_script_lines))
        # In the Dockerfile, copy the script and set it as the ENTRYPOINT.
        dockerfile_content.append("COPY firewall_setup.sh /firewall_setup.sh")
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
