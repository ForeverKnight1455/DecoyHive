import socket
import psutil
import subprocess
import logging
import platform
import os

# Configure logging
logging.basicConfig(
    filename='honeypot.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def get_running_services():
    """Collect running services and open ports."""
    services = []
    try:
        for conn in psutil.net_connections(kind='inet'):
            if conn.status == psutil.CONN_LISTEN:
                try:
                    service_name = socket.getservbyport(conn.laddr.port)
                    process_name = psutil.Process(conn.pid).name()
                    services.append({
                        "port": conn.laddr.port,
                        "service": service_name,
                        "pid": conn.pid,
                        "process_name": process_name
                    })
                    logging.info(f"Detected service: {service_name} on port {conn.laddr.port}, process: {process_name}")
                except (OSError, psutil.NoSuchProcess, psutil.AccessDenied) as e:
                    logging.warning(f"Error fetching service info: {e}")
    except Exception as e:
        logging.error(f"Failed to retrieve running services: {e}")
    return services

def get_filtered_software_from_running_services():
    """Get installed software based on running services."""
    installed_software = get_installed_software()
    running_services = [service["process_name"] for service in get_running_services()]
    return [s for s in installed_software if any(rs in s for rs in running_services)]


def run_command(command):
    """Helper function to run a shell command and log errors."""
    try:
        result = subprocess.run(command, capture_output=True, text=True, check=True)
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        logging.error(f"Command '{' '.join(command)}' failed: {e}")
    except FileNotFoundError:
        logging.error(f"Command not found: {command}")
    except Exception as e:
        logging.error(f"Unexpected error running command '{' '.join(command)}': {e}")
    return ""

def get_network_info():
    """Collect network configuration information."""
    return {
        "ip_address": run_command(["hostname", "-I"]),
        "routing_table": run_command(["netstat", "-r"]),
        "dns_servers": run_command(["cat", "/etc/resolv.conf"]),
        "firewall_rules": run_command(["iptables", "-L"])
    }

def get_user_info():
    """Collect user and permission information."""
    return {
        "users": run_command(["cat", "/etc/passwd"]),
        "groups": run_command(["cat", "/etc/group"]),
        "sudoers": run_command(["cat", "/etc/sudoers"])
    }

def get_environment_variables():
    """Collect environment variables."""
    try:
        return {
            "system_env": dict(os.environ),
        }
    except Exception as e:
        logging.error(f"Error retrieving environment variables: {e}")
        return {}

def get_cron_jobs():
    """Collect cron jobs and scheduled tasks."""
    try:
        return {"cron_jobs": run_command(["crontab", "-l"])}
    except Exception as e:
        logging.error(f"Error collecting cron jobs: {e}")
        return {"cron_jobs": []}

def get_log_files():
    """Collect system logs."""
    return {
        "syslog": run_command(["cat", "/var/log/syslog"]),
        "auth_log": run_command(["cat", "/var/log/auth.log"]),
        "application_logs": run_command(["ls", "/var/log"])
    }

def get_installed_software_linux():
    """Get a list of installed software on Linux using the appropriate package manager."""
    results = {"debian": [], "rhl": [], "arch": [], "gentoo": []}
    try:
        if os.path.exists('/usr/bin/dpkg'):
            logging.info("Detecting Debian-based software...")
            results["debian"] = run_command(['dpkg', '--list']).splitlines()
        if os.path.exists('/bin/rpm'):
            logging.info("Detecting Red Hat-based software...")
            results["rhl"] = run_command(['rpm', '-qa']).splitlines()
        if os.path.exists('/usr/bin/pacman'):
            logging.info("Detecting Arch-based software...")
            results["arch"] = run_command(['pacman', '-Q']).splitlines()
        if os.path.exists('/usr/bin/emerge'):
            logging.info("Detecting Gentoo-based software...")
            results["gentoo"] = run_command(['equery', 'list', '*']).splitlines()
    except Exception as e:
        logging.error(f"Error detecting installed software: {e}")

    if any(results.values()):
        return results
    else:
        logging.warning("Unsupported Linux distribution")
        return "Unsupported Linux distribution"

def get_installed_software():
    """Detect OS and get installed software accordingly."""
    try:
        system = platform.system()
        logging.info(f"Detected OS: {system}")

        if system == "Windows":
            logging.info("Detecting Windows software...")
            return "Windows detection not implemented in this version."
        elif system == "Linux":
            return get_installed_software_linux()
        else:
            logging.warning("Unsupported OS")
            return "Unsupported OS"
    except Exception as e:
        logging.error(f"Error detecting installed software: {e}")
        return "Error detecting installed software"
