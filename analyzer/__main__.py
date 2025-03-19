import json
import logging
import os
import sys

from utils import (
    get_os_info, get_hardware_info, get_running_services, get_network_info,
    get_user_info, get_filtered_software_from_running_services,
    get_environment_variables, get_cron_jobs, get_log_files,
    generate_dockerfile, docker_run
)

# Enforce root privileges
if os.getuid() != 0:
    print("This script must be run as root. Please use 'sudo' or switch to the root user.")
    sys.exit(1)

def load_config():
    default_config = {
        "export_config_directory": "./config_exports",
        "log_file": "app.log",
        "log_level": "INFO",
        "enable_service_monitoring": True,
        "enable_network_monitoring": True,
        "enable_user_monitoring": True,
        "enable_software_monitoring": True
    }
    config_path = "settings.json"
    if os.path.exists(config_path):
        try:
            with open(config_path, "r") as f:
                return json.load(f)
        except json.JSONDecodeError as e:
            logging.error(f"Error parsing settings.json: {e}")
    return default_config

config = load_config()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("honeypot.log"),  # Log to file
        logging.StreamHandler()  # Log to terminal
    ]
)

def save_config():
    """Save collected data to a config file."""
    config_data = {}

    if config.get("enable_service_monitoring", True):
        config_data["services"] = get_running_services()
    if config.get("enable_network_monitoring", True):
        config_data["network"] = get_network_info()
    if config.get("enable_user_monitoring", True):
        config_data["users"] = get_user_info()
    if config.get("enable_software_monitoring", True):
        config_data["software"] = get_filtered_software_from_running_services()

    config_data.update({
        "hardware": get_hardware_info(),
        "os": get_os_info(),
        "env_vars": get_environment_variables(),
        "cron_jobs": get_cron_jobs(),
        "logs": get_log_files()
    })

    export_path = config.get("export_config_directory", "./config_exports")
    os.makedirs(export_path, exist_ok=True)
    filename = os.path.join(export_path, "config.json")

    logging.info("Saving config to file")
    with open(filename, "w") as f:
        json.dump(config_data, f, indent=2)

if __name__ == "__main__":
    # Collect configuration and generate Dockerfile
    save_config()
    generate_dockerfile("./config_exports/config.json")
    
    # Call the docker_run module's main() to build, run, and manage the container lifecycle.
    # The script will run continuously and upon exit, the container will be stopped and removed.
    docker_run.main()
