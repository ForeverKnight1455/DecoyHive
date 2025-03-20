from .hw_info import *
from .os_info import *
from .net_info import *
from .software_info import *
from .docker_generator import *
from .docker_run import *

import os
import json
import logging
from email.policy import default

default_config = {
    "export_config_directory": "./config_exports",
    "output_directory" : "./output",
    "log_file": "app.log",
    "logs_directory":"./logs",
    "log_level": "INFO",
    "enable_service_monitoring": True,
    "enable_network_monitoring": True,
    "enable_user_monitoring": True,
    "enable_software_monitoring": True
}
config_path = "settings.json"



def load_config():
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


#create folder if not exist logs and output
if not os.path.exists(default_config['output_directory']):
    os.makedirs(default_config['output_directory'])
if not os.path.exists(default_config['logs_directory']):
    os.makedirs(default_config['logs_directory'])
