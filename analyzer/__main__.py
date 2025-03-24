import json
import logging
import os
import sys

from utils import (
    get_os_info, get_hardware_info, get_running_services, get_network_info,
    get_user_info, get_filtered_software_from_running_services,
    get_environment_variables, get_cron_jobs, get_log_files,
    generate_dockerfile, docker_run, get_services_from_nmap
)

def get_project_root():
    """Get the project root directory."""
    # Get the directory containing this file
    current_dir = os.path.dirname(os.path.abspath(__file__))
    # Go up one level to get to the project root
    return os.path.dirname(current_dir)

def load_config():
    project_root = get_project_root()
    default_config = {
        "export_config_directory": "config_exports",  # Changed to relative path
        "output_directory": "output",  # Changed to relative path
        "log_file": "app.log",
        "logs_directory": "logs",
        "log_level": "INFO",
        "enable_service_monitoring": True,
        "enable_network_monitoring": True,
        "enable_user_monitoring": True,
        "enable_software_monitoring": True,
        "enable_port_scanning": True,
        "scan_target": "localhost"
    }
    config_path = os.path.join(project_root, "settings.json")
    if os.path.exists(config_path):
        try:
            with open(config_path, "r") as f:
                return json.load(f)
        except json.JSONDecodeError as e:
            logging.error(f"Error parsing settings.json: {e}")
    else:
        try:
            with open(config_path, "w") as f:
                f.write(json.dumps(default_config))
        except Exception as e:
            logging.error(f"Error parsing settings.json: {e}")

    return default_config

config = load_config()

# Create all necessary directories
project_root = get_project_root()
for directory in [config['output_directory'], config['logs_directory'], config['export_config_directory']]:
    full_path = os.path.join(project_root, directory)
    if not os.path.exists(full_path):
        os.makedirs(full_path)
        logging.info(f"Created directory: {full_path}")

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
    if config.get("enable_port_scanning", True):
        config_data["ports"] = get_services_from_nmap(config.get("scan_target", "localhost"))

    config_data.update({
        "hardware": get_hardware_info(),
        "os": get_os_info(),
        "env_vars": get_environment_variables(),
        "cron_jobs": get_cron_jobs(),
        "logs": get_log_files()
    })

    export_path = os.path.join(project_root, config.get("export_config_directory", "config_exports"))
    os.makedirs(export_path, exist_ok=True)
    filename = os.path.join(export_path, "config.json")

    logging.info(f"Saving config to file: {filename}")
    with open(filename, "w") as f:
        json.dump(config_data, f, indent=2)

if __name__ == "__main__":
    # Collect configuration and generate Dockerfile
    save_config()
    
    # Generate Dockerfile with correct paths
    config_file = os.path.join(config['export_config_directory'], "config.json")
    output_dir = config['output_directory']
    
    if os.path.exists(config_file):
        generate_dockerfile(config_file, output_dir)
        logging.info(f"Generated Dockerfile in {output_dir}")
    else:
        logging.error(f"Config file not found at {config_file}")

    # Call the docker_run module's main() to build, run, and manage the container lifecycle.
    # The script will run continuously and upon exit, the container will be stopped and removed.
    docker_run.main()
