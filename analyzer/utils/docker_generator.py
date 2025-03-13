import json
import os

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

def generate_dockerfile(json_file, output_file="Dockerfile"):
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

    else:
        dockerfile_content.extend([
            "# Install Chocolatey",
            "RUN powershell -Command Set-ExecutionPolicy Bypass -Scope Process -Force; \"",
            "iex ((New-Object System.Net.WebClient).DownloadString('https://chocolatey.org/install.ps1'))",
            "RUN setx /M PATH \"%PATH%;C:\\ProgramData\\chocolatey\\bin\"",
            ""
        ])

    software = config.get("software", [])
    packages = []

    if isinstance(software, dict):
        if is_windows:
            packages = software.get("windows", [])
        else:
            packages = software.get("debian", []) if "apt" in package_manager else \
                      software.get("rhl", []) if "yum" in package_manager or "dnf" in package_manager else \
                      software.get("arch", []) if "pacman" in package_manager else \
                      software.get("alpine", []) if "apk" in package_manager else []
    elif isinstance(software, list):
        packages = software

    if packages:
        package_list = " ".join(packages)
        dockerfile_content.extend([
            "# Install required software packages",
            f"RUN {install_cmd} {package_list}",
            ""
        ])

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

    env_vars = config.get("env_vars", {}).get("system_env", {})
    sensitive_keys = {"PASSWORD", "SECRET", "TOKEN", "API_KEY"}
    for key, value in env_vars.items():
        if not any(s in key.upper() for s in sensitive_keys):
            value = value.replace("\\", "/").rstrip("/")
            dockerfile_content.append(f'ENV {key}="{value}"')

    network_config = config.get("network", {})
    if network_config and not is_windows:
        dockerfile_content.append("\n# Configure networking")
        if "ip_address" in network_config:
            dockerfile_content.append(f'RUN echo "IP Address: {network_config["ip_address"]}"')

    firewall_rules = network_config.get("firewall_rules", "").split("\n")
    if firewall_rules and not is_windows:
        dockerfile_content.append("# Configure firewall rules")
        for rule in firewall_rules:
            if rule.strip():
                dockerfile_content.append(f"RUN iptables {rule}")

    services = config.get("services", [])
    if services and not is_windows:
        dockerfile_content.append("\n# Enable system services")
        for service in services:
            dockerfile_content.append(f"RUN systemctl enable {service['process_name']} || true")

    if is_windows:
        dockerfile_content.append('\nCMD ["cmd", "/c", "ping", "-t", "localhost", ">", "NUL"]')
    else:
        dockerfile_content.append('\nCMD ["tail", "-f", "/dev/null"]')

    with open(output_file, "w") as f:
        f.write("\n".join(dockerfile_content))

    print(f"Dockerfile generated successfully as {output_file}")

if __name__ == "__main__":
    generate_dockerfile("config_export/config.json")
