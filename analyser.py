import platform
import subprocess
import re
import psutil
import json
import os
from datetime import datetime

def get_system_info():
    system_info = {
        "os_info": get_os_info(),
        "cpu_info": get_cpu_info(),
        "memory_info": get_memory_info(),
        "disk_info": get_disk_info(),
        "network_info": get_network_info(),
        "installed_packages": get_installed_packages()
    }
    return system_info

def get_os_info():
    os_name = platform.system()
    if os_name == "Linux":
        return {
            "system": "Linux",
            "distribution": get_linux_distro(),
            "kernel": platform.release(),
            "architecture": platform.machine(),
            "processor": platform.processor()
        }
    elif os_name == "Windows":
        return {
            "system": "Windows",
            "version": platform.version(),
            "release": platform.release(),
            "architecture": platform.machine(),
            "processor": platform.processor()
        }
    else:
        return {
            "system": os_name,
            "version": platform.version(),
            "architecture": platform.machine(),
            "processor": platform.processor()
        }

def get_cpu_info():
    return {
        "physical_cores": psutil.cpu_count(logical=False),
        "total_cores": psutil.cpu_count(logical=True),
        "max_frequency": f"{psutil.cpu_freq().max:.2f}MHz" if psutil.cpu_freq() else "Unknown",
        "current_frequency": f"{psutil.cpu_freq().current:.2f}MHz" if psutil.cpu_freq() else "Unknown",
        "cpu_usage_per_core": [f"{percentage:.1f}%" for percentage in psutil.cpu_percent(percpu=True)],
        "total_cpu_usage": f"{psutil.cpu_percent()}%"
    }

def get_memory_info():
    memory = psutil.virtual_memory()
    return {
        "total": f"{memory.total / (1024**3):.2f}GB",
        "available": f"{memory.available / (1024**3):.2f}GB",
        "used": f"{memory.used / (1024**3):.2f}GB",
        "percentage": f"{memory.percent}%"
    }

def get_disk_info():
    disks = {}
    for partition in psutil.disk_partitions():
        try:
            partition_usage = psutil.disk_usage(partition.mountpoint)
            disks[partition.mountpoint] = {
                "device": partition.device,
                "filesystem": partition.fstype,
                "total": f"{partition_usage.total / (1024**3):.2f}GB",
                "used": f"{partition_usage.used / (1024**3):.2f}GB",
                "free": f"{partition_usage.free / (1024**3):.2f}GB",
                "percentage": f"{partition_usage.percent}%"
            }
        except:
            continue
    return disks

def get_network_info():
    network_info = {}
    for interface, addresses in psutil.net_if_addrs().items():
        network_info[interface] = []
        for addr in addresses:
            network_info[interface].append({
                "address": addr.address,
                "netmask": addr.netmask,
                "family": str(addr.family)
            })
    return network_info

def get_installed_packages():
    packages = {}
    
    if platform.system() == "Linux":
        try:
            # For Debian/Ubuntu systems
            output = subprocess.check_output(["dpkg", "-l"]).decode()
            packages["dpkg"] = [line.split()[1:3] for line in output.split("\n")[5:] if line and not line.startswith("rc")]
        except:
            try:
                # For Red Hat/CentOS systems
                output = subprocess.check_output(["rpm", "-qa"]).decode()
                packages["rpm"] = output.split("\n")
            except:
                packages["error"] = "Could not detect installed packages"
    elif platform.system() == "Windows":
        try:
            output = subprocess.check_output(["wmic", "product", "get", "name,version"]).decode()
            packages["windows"] = [line.split()[:2] for line in output.split("\n")[1:] if line.strip()]
        except:
            packages["error"] = "Could not detect installed packages"
    
    return packages

def get_linux_distro():
    """Detect Linux distribution and version"""
    try:
        # Try reading from os-release first
        with open("/etc/os-release", "r") as f:
            lines = f.readlines()
            distro_info = {}
            for line in lines:
                if "=" in line:
                    key, value = line.strip().split("=", 1)
                    distro_info[key] = value.strip('"')
            
            distro_name = distro_info.get("NAME", "Unknown")
            distro_version = distro_info.get("VERSION_ID", "latest")
            return f"{distro_name} {distro_version}"
    except FileNotFoundError:
        try:
            # Try lsb_release command
            output = subprocess.check_output(["lsb_release", "-ds"]).decode().strip()
            return output
        except:
            try:
                # Try reading from system-release
                with open("/etc/system-release", "r") as f:
                    return f.read().strip()
            except:
                return "Unknown Linux Distribution"

def save_system_info(system_info):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"system_info_{timestamp}.json"
    
    with open(filename, "w") as f:
        json.dump(system_info, f, indent=4)
    return filename

def generate_dockerfile(system_info):
    """Generate a Dockerfile based on detected system information"""
    os_info = system_info["os_info"]
    
    if os_info["system"] == "Linux":
        # Get distribution details
        distro_full = os_info["distribution"].lower()
        
        # Handle different distributions
        if "ubuntu" in distro_full:
            base_image = "ubuntu"
            package_manager = "apt-get"
            install_cmd = f"{package_manager} update && {package_manager} install -y"
            cleanup_cmd = "rm -rf /var/lib/apt/lists/*"
        elif "debian" in distro_full:
            base_image = "debian"
            package_manager = "apt-get"
            install_cmd = f"{package_manager} update && {package_manager} install -y"
            cleanup_cmd = "rm -rf /var/lib/apt/lists/*"
        elif "centos" in distro_full or "rhel" in distro_full:
            base_image = "centos"
            package_manager = "yum"
            install_cmd = f"{package_manager} update -y && {package_manager} install -y"
            cleanup_cmd = f"{package_manager} clean all"
        elif "fedora" in distro_full:
            base_image = "fedora"
            package_manager = "dnf"
            install_cmd = f"{package_manager} update -y && {package_manager} install -y"
            cleanup_cmd = f"{package_manager} clean all"
        else:
            # Default to Ubuntu if distribution is not recognized
            base_image = "ubuntu"
            package_manager = "apt-get"
            install_cmd = f"{package_manager} update && {package_manager} install -y"
            cleanup_cmd = "rm -rf /var/lib/apt/lists/*"

        # Extract version from distribution string
        version = next((part for part in distro_full.split() if part[0].isdigit()), "latest")
        
        dockerfile_content = f"""# Dockerfile generated based on system analysis
FROM {base_image}:{version}

# System information at the time of generation:
# OS: {os_info["distribution"]}
# CPU Cores: {system_info["cpu_info"]["total_cores"]}
# Memory: {system_info["memory_info"]["total"]}
# Architecture: {os_info["architecture"]}

# Update system and install basic utilities
RUN {install_cmd} \\
    curl \\
    wget \\
    vim \\
    htop \\
    net-tools \\
    python3 \\
    python3-pip \\
    && {cleanup_cmd}

# Set environment variables
ENV PYTHONUNBUFFERED=1

# Create working directory
WORKDIR /app

# Copy application files
COPY . /app/

# Install Python dependencies (if requirements.txt exists)
RUN if [ -f requirements.txt ]; then pip3 install -r requirements.txt; fi

# Default command
CMD ["bash"]
"""
    
    elif os_info["system"] == "Windows":
        windows_version = os_info["version"]
        # Determine Windows version and choose appropriate base image
        if "10.0" in windows_version:
            base_image = "mcr.microsoft.com/windows/servercore:ltsc2022"
        else:
            base_image = "mcr.microsoft.com/windows/servercore:ltsc2019"

        dockerfile_content = f"""# Dockerfile generated based on system analysis
FROM {base_image}

# System information at the time of generation:
# OS: Windows {os_info["version"]}
# CPU Cores: {system_info["cpu_info"]["total_cores"]}
# Memory: {system_info["memory_info"]["total"]}
# Architecture: {os_info["architecture"]}

# Install Chocolatey
RUN powershell -Command \\
    Set-ExecutionPolicy Bypass -Scope Process -Force; \\
    [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.SecurityProtocolType]::Tls12; \\
    iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))

# Install basic tools using Chocolatey
RUN choco install -y python3 git wget curl

# Create working directory
WORKDIR C:\\app

# Copy application files
COPY . C:\\app\\

# Install Python dependencies (if requirements.txt exists)
RUN if exist requirements.txt pip install -r requirements.txt

# Default command
CMD ["powershell"]
"""
    
    else:  # Default to Ubuntu for unsupported OS
        dockerfile_content = f"""# Dockerfile generated for unsupported OS ({os_info["system"]})
FROM ubuntu:latest

# System information at the time of generation:
# OS: {os_info["system"]} {os_info["version"]}
# CPU Cores: {system_info["cpu_info"]["total_cores"]}
# Memory: {system_info["memory_info"]["total"]}
# Architecture: {os_info["architecture"]}

# Update system and install basic utilities
RUN apt-get update && apt-get install -y \\
    curl \\
    wget \\
    vim \\
    htop \\
    net-tools \\
    python3 \\
    python3-pip \\
    && rm -rf /var/lib/apt/lists/*

# Set environment variables
ENV PYTHONUNBUFFERED=1

# Create working directory
WORKDIR /app

# Copy application files
COPY . /app/

# Install Python dependencies (if requirements.txt exists)
RUN if [ -f requirements.txt ]; then pip3 install -r requirements.txt; fi

# Default command
CMD ["bash"]
"""

    with open("Dockerfile", "w") as f:
        f.write(dockerfile_content)

def main():
    print("Collecting system information...")
    system_info = get_system_info()
    
    # Save system information to JSON file
    info_file = save_system_info(system_info)
    print(f"System information saved to {info_file}")
    
    # Generate Dockerfile
    generate_dockerfile(system_info)
    print("Dockerfile generated successfully!")
    
    # Print summary
    print("\nSystem Summary:")
    print(f"OS: {system_info['os_info']['system']}")
    if system_info['os_info']['system'] == 'Linux':
        print(f"Distribution: {system_info['os_info']['distribution']}")
    print(f"CPU Cores: {system_info['cpu_info']['total_cores']}")
    print(f"Memory: {system_info['memory_info']['total']}")
    print(f"CPU Usage: {system_info['cpu_info']['total_cpu_usage']}")

if __name__ == "__main__":
    main()