import platform
import subprocess
import re

def detect_os():
    os_name = platform.system()
    if os_name == "Linux":
        return "Linux", get_linux_distro()
    else:
        return os_name, platform.version()

def get_linux_distro():
    try:
        with open("/etc/os-release", "r") as f:
            lines = f.readlines()
            distro_info = {}
            for line in lines:
                if "=" in line:
                    key, value = line.strip().split("=")
                    distro_info[key] = value.strip('"')
            distro_name = distro_info.get("NAME", "Unknown")
            distro_version = distro_info.get("VERSION_ID", "Unknown")
            return f"{distro_name} {distro_version}"
    except FileNotFoundError:
        return "Unknown Linux Distribution"

def save_details(os_name, os_version):
    with open("os_details.txt", "w") as f:
        f.write(f"Operating System: {os_name}\n")
        f.write(f"Version: {os_version}\n")

def generate_dockerfile(os_name, os_version):
    if os_name == "Linux":
        # Extract the Linux distribution name (e.g., Ubuntu, CentOS)
        distro_name = os_version.split()[0].lower()
        distro_version = os_version.split()[1] if len(os_version.split()) > 1 else "latest"

        # Create a Dockerfile for the detected Linux distribution
        dockerfile_content = f"""
# Dockerfile for {os_version}
FROM {distro_name}:{distro_version}

# Update and install basic tools
RUN apt-get update && apt-get install -y \\
    curl \\
    wget \\
    vim \\
    && rm -rf /var/lib/apt/lists/*
"""
    elif os_name == "Windows":
        # Dockerfile for Windows (not commonly used, but as an example)
        dockerfile_content = """
# Dockerfile for Windows
# Note: Windows containers require a Windows host and Docker Desktop with Windows containers enabled.
FROM mcr.microsoft.com/windows/servercore:ltsc2022

# Install Chocolatey (Windows package manager)
RUN powershell -Command \\
    Set-ExecutionPolicy Bypass -Scope Process -Force; \\
    [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.SecurityProtocolType]::Tls12; \\
    iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))
"""
    elif os_name == "Darwin":  # macOS
        # Dockerfile for macOS (not directly supported, but you can use a Linux base image)
        dockerfile_content = """
# Dockerfile for macOS
# Note: macOS does not support Docker containers natively. Use a Linux base image.
FROM ubuntu:latest

# Update and install basic tools
RUN apt-get update && apt-get install -y \\
    curl \\
    wget \\
    vim \\
    && rm -rf /var/lib/apt/lists/*
"""
    else:
        dockerfile_content = """
# Dockerfile for Unknown OS
# Using a generic Linux base image
FROM ubuntu:latest

# Update and install basic tools
RUN apt-get update && apt-get install -y \\
    curl \\
    wget \\
    vim \\
    && rm -rf /var/lib/apt/lists/*
"""

    # Save the Dockerfile
    with open("Dockerfile", "w") as f:
        f.write(dockerfile_content)

def main():
    os_name, os_version = detect_os()
    save_details(os_name, os_version)
    generate_dockerfile(os_name, os_version)
    print(f"Operating System: {os_name}")
    print(f"Version: {os_version}")
    print("Dockerfile generated successfully!")

if __name__ == "__main__":
    main()