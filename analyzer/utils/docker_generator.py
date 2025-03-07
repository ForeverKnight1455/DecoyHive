import json
import os
import platform

def generate_dockerfile(json_file, output_file="Dockerfile"):
    """Generate a Dockerfile from JSON configuration"""
    with open(json_file, "r") as f:
        raw_config = json.load(f)
    
    # Ensure we're working with a dictionary
    config = {}
    if isinstance(raw_config, list):
        # If it's a list, merge all dictionaries into one
        for item in raw_config:
            if isinstance(item, dict):
                config.update(item)
    else:
        config = raw_config if isinstance(raw_config, dict) else {}
    
    # Default values if keys don't exist
    os_info = config.get("os", {})
    if not isinstance(os_info, dict):
        os_info = {}
    
    os_version = os_info.get("os_version", "latest").lower()
    
    software = config.get("software", {})
    if not isinstance(software, dict):
        software = {}
    
    # Use platform-specific settings
    if platform.system() == "Windows":
        base_image = "ubuntu:20.04"  # Use Ubuntu on Windows for WSL2 compatibility
    else:
        # For Linux hosts
        if "ubuntu" in os_version:
            base_image = f"ubuntu:{os_version.replace('ubuntu ', '').strip()}"
        elif "debian" in os_version:
            base_image = f"debian:{os_version.replace('debian ', '').strip()}"
        elif "alpine" in os_version:
            base_image = f"alpine:{os_version.replace('alpine ', '').strip()}"
        else:
            base_image = "ubuntu:20.04"  # Use a specific version instead of latest
    
    dockerfile_content = [
        f"FROM {base_image}",  # Remove the --platform flag
        'LABEL maintainer="DecoyHive"',
        "",
        "# Set environment variables to avoid interactive prompts",
        "ENV DEBIAN_FRONTEND=noninteractive",
        "",
        "# Update and install packages",
        "RUN apt-get update && apt-get install -y \\",
        "    net-tools \\",
        "    iptables \\",
        "    iproute2 && \\",
        "    rm -rf /var/lib/apt/lists/*",
        ""
    ]
    
    # Add any additional packages
    packages = software.get("debian", [])
    if packages:
        package_list = " ".join(packages)
        dockerfile_content.extend([
            "# Install additional packages",
            "RUN apt-get update && \\",
            f"    apt-get install -y {package_list} && \\",
            "    rm -rf /var/lib/apt/lists/*",
            ""
        ])
    
    # Add users
    users_config = config.get("users", {})
    if isinstance(users_config, dict):
        users = users_config.get("users", "root:x:0:0:root:/root:/bin/bash").split("\n")
    else:
        users = ["root:x:0:0:root:/root:/bin/bash"]
    
    # List of system users that typically exist in base images
    system_users = {
        'root', 'daemon', 'bin', 'sys', 'sync', 'games', 'man', 'lp', 'mail',
        'news', 'uucp', 'proxy', 'www-data', 'backup', 'list', 'irc',
        'gnats', 'nobody', 'systemd-network', 'systemd-resolve',
        'systemd-timesync', '_apt', 'messagebus', 'syslog'
    }

    for user in users:
        parts = user.split(":")
        if len(parts) >= 7:
            username = parts[0]
            home_dir = parts[5]
            shell = parts[6]
            # Skip system users that already exist
            if username not in system_users:
                dockerfile_content.append(f"RUN useradd -m -d {home_dir} -s {shell} {username}")
    
    # Add environment variables, excluding sensitive data
    env_vars = config.get("env_vars", {})
    if isinstance(env_vars, dict):
        system_env = env_vars.get("system_env", {})
        if system_env:
            dockerfile_content.append("\n# Set environment variables")
            sensitive_vars = {'SSH_AUTH_SOCK', 'SSH_PRIVATE_KEY', 'PASSWORD', 
                            'SECRET', 'TOKEN', 'API_KEY', 'CREDENTIALS'}
            for key, value in system_env.items():
                # Skip sensitive environment variables
                if not any(sensitive in key.upper() for sensitive in sensitive_vars):
                    value = str(value).replace('"', '\\"')
                    dockerfile_content.append(f'ENV {key}="{value}"')
    
    # Add CMD to keep container running
    dockerfile_content.extend([
        "",
        "# Keep container running",
        'CMD ["tail", "-f", "/dev/null"]'
    ])
    
    # Write the Dockerfile
    with open(output_file, "w") as f:
        f.write("\n".join(dockerfile_content))
    
    print(f"Dockerfile generated successfully as {output_file}")

