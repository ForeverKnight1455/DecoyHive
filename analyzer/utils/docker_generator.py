import json
import os

def detect_base_image(os_version):
    """Detects the correct base image and package manager."""
    os_version = os_version.lower()
    
    # Check for Windows first
    if "windows" in os_version:
        # Windows Server Core images
        if "2019" in os_version:
            return "mcr.microsoft.com/windows/servercore:ltsc2019", "choco", "choco", "choco install -y"
        elif "2022" in os_version:
            return "mcr.microsoft.com/windows/servercore:ltsc2022", "choco", "choco", "choco install -y"
        else:
            # Default to latest Windows Server Core
            return "mcr.microsoft.com/windows/servercore:latest", "choco", "choco", "choco install -y"
    
    # Linux distributions
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
        return "ubuntu:20.04", "apt-get", "apt-get update", "apt-get install -y"  # Default to Ubuntu

def generate_dockerfile(json_file, output_file="Dockerfile"):
    """Generates a Dockerfile for creating a system clone."""
    
    with open(json_file, "r") as f:
        config = json.load(f)

    # Get OS details
    os_info = config.get("os", {})
    os_version = os_info.get("os_version", "ubuntu 20.04")

    # Detect correct base image and package manager
    base_image, package_manager, update_cmd, install_cmd = detect_base_image(os_version)

    # Check if it's a Windows-based system
    is_windows = "windows" in os_version.lower()

    dockerfile_content = [
        f"FROM {base_image}",
        'LABEL maintainer="SystemClone"',
        ""
    ]

    if not is_windows:
        # Linux-specific configurations
        dockerfile_content.extend([
            "# Set non-interactive mode (for Debian-based systems)",
            "ENV DEBIAN_FRONTEND=noninteractive",
            "",
            f"# Update system packages",
            f"RUN {update_cmd}",
            ""
        ])
    else:
        # Windows-specific configurations
        dockerfile_content.extend([
            "# Install Chocolatey package manager",
            "RUN powershell -Command Set-ExecutionPolicy Bypass -Scope Process -Force; [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072; iex ((New-Object System.Net.WebClient).DownloadString('https://chocolatey.org/install.ps1'))",
            "",
            "# Add Chocolatey to PATH",
            "RUN setx /M PATH \"%PATH%;C:\\ProgramData\\chocolatey\\bin\"",
            ""
        ])

    # Install software packages
    software = config.get("software", [])
    packages = []
    
    if isinstance(software, dict):
        if is_windows:
            packages = software.get("windows", [])  # Get Windows-specific packages
        else:
            packages = software.get("debian", []) if "apt" in package_manager else \
                      software.get("rhl", []) if "yum" in package_manager or "dnf" in package_manager else \
                      software.get("arch", []) if "pacman" in package_manager else \
                      software.get("alpine", []) if "apk" in package_manager else []
    elif isinstance(software, list):
        packages = software

    if packages:
        package_list = " ".join(packages)
        if is_windows:
            dockerfile_content.extend([
                "# Install system packages using Chocolatey",
                f"RUN {install_cmd} {package_list}",
                ""
            ])
        else:
            dockerfile_content.extend([
                "# Install system packages",
                f"RUN {install_cmd} {package_list}",
                ""
            ])

    # Add only non-system users (skip service accounts and system users)
    if not is_windows:
        users_config = config.get("users", {}).get("users", "").split("\n")
        for user in users_config:
            parts = user.split(":")
            if len(parts) >= 7:
                username = parts[0]
                uid = int(parts[2]) if parts[2].isdigit() else 0
                home_dir = parts[5]
                shell = parts[6]
                
                # Skip system users and service accounts:
                # 1. Users starting with underscore (_) are service accounts
                # 2. Users with UID < 1000 are typically system users
                # 3. Users with /usr/sbin/nologin or /bin/false shells are service accounts
                # 4. Users with /nonexistent home are service accounts
                if not username.startswith('_') and \
                   uid >= 1000 and \
                   shell not in ['/usr/sbin/nologin', '/bin/false'] and \
                   home_dir != '/nonexistent':
                    dockerfile_content.append(f"RUN useradd -m -d {home_dir} -s {shell} {username}")

    # Set environment variables (excluding sensitive ones)
    env_vars = config.get("env_vars", {}).get("system_env", {})
    sensitive_keys = {"PASSWORD", "SECRET", "TOKEN", "API_KEY"}
    for key, value in env_vars.items():
        if not any(s in key.upper() for s in sensitive_keys):
            if isinstance(value, str):
                if is_windows:
                    # Keep Windows-style paths for Windows containers
                    value = value.rstrip("\\")
                else:
                    # Convert to Unix-style paths for Linux containers
                    value = value.replace("\\", "/").rstrip("/")
            dockerfile_content.append(f'ENV {key}="{value}"')

    # Set up networking configurations
    network_config = config.get("network", {})
    if network_config and not is_windows:  # Skip network configuration for Windows
        dockerfile_content.append("\n# Configure networking")
        if "ip_address" in network_config:
            dockerfile_content.append(f'RUN echo "IP Address: {network_config["ip_address"]}"')

    # Set firewall rules (skip for Windows as it uses different firewall management)
    if not is_windows:
        firewall_rules = network_config.get("firewall_rules", "").split("\n")
        if firewall_rules:
            dockerfile_content.append("# Configure firewall rules")
            for rule in firewall_rules:
                if rule.strip():
                    dockerfile_content.append(f"RUN iptables {rule}")

    # Enable system services (skip for Windows as it uses different service management)
    if not is_windows:
        services = config.get("services", [])
        if services:
            dockerfile_content.append("\n# Enable system services")
            for service in services:
                dockerfile_content.append(f"RUN systemctl enable {service['process_name']} || true")

    # Keep container running
    if is_windows:
        dockerfile_content.append('\nCMD ["cmd", "/c", "ping", "-t", "localhost", ">", "NUL"]')
    else:
        dockerfile_content.append('\nCMD ["tail", "-f", "/dev/null"]')

    # Write the Dockerfile
    with open(output_file, "w") as f:
        f.write("\n".join(dockerfile_content))
    
    print(f"Dockerfile generated successfully as {output_file}")


# Example usage:
if __name__ == "__main__":
    generate_dockerfile("config_export/config.json")
