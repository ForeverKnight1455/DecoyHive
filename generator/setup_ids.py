import os
import subprocess

# Paths for configuration files
CONFIG_DIR = "./ids_config"
SNORT_RULES_PATH = f"{CONFIG_DIR}/snort.rules"
LOKI_CONFIG_PATH = f"{CONFIG_DIR}/loki-config.yml"
GRAFANA_DATASOURCE_PATH = f"{CONFIG_DIR}/grafana-datasource.yml"

# Create necessary directories
os.makedirs(CONFIG_DIR, exist_ok=True)

# Snort Rules
snort_rules = """
alert icmp any any -> any any (msg:"ICMP Packet detected"; sid:1000001;)
"""
with open(SNORT_RULES_PATH, "w") as f:
    f.write(snort_rules)

# Loki Configuration
loki_config = """
auth_enabled: false
server:
  http_listen_port: 3100
positions:
  filename: /tmp/positions.yaml
clients:
  - url: http://loki:3100/loki/api/v1/push
"""
with open(LOKI_CONFIG_PATH, "w") as f:
    f.write(loki_config)

# Grafana Data Source (Loki Integration)
grafana_datasource = """
apiVersion: 1
datasources:
  - name: Loki
    type: loki
    access: proxy
    url: http://loki:3100
    isDefault: true
"""
with open(GRAFANA_DATASOURCE_PATH, "w") as f:
    f.write(grafana_datasource)

# Docker Compose File
docker_compose_content = f"""
version: "3.8"

services:
  snort:
    image: cturra/snort
    container_name: snort
    restart: unless-stopped
    network_mode: "host"
    volumes:
      - {SNORT_RULES_PATH}:/etc/snort/rules/local.rules
    command: ["-A", "fast", "-q", "-c", "/etc/snort/snort.conf", "-i", "eth0"]

  loki:
    image: grafana/loki:2.8.2
    container_name: loki
    ports:
      - "3100:3100"
    volumes:
      - {LOKI_CONFIG_PATH}:/etc/loki/config.yml
    command: -config.file=/etc/loki/config.yml
    restart: unless-stopped

  grafana:
    image: grafana/grafana:latest
    container_name: grafana
    ports:
      - "3000:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin
    volumes:
      - {GRAFANA_DATASOURCE_PATH}:/etc/grafana/provisioning/datasources/datasource.yml
    restart: unless-stopped
"""

with open("docker-compose.yml", "w") as f:
    f.write(docker_compose_content)

# Start Docker containers
print("Starting IDS system...")
subprocess.run(["docker", "compose", "up", "-d"], check=True)

print("IDS system is now running with Snort, Loki, and Grafana.")
