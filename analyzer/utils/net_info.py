import subprocess

def get_network_info():
    """Collect network configuration information."""
    return {
        "ip_address": subprocess.run(["hostname", "-I"], capture_output=True, text=True).stdout.strip(),
        "routing_table": subprocess.run(["netstat", "-r"], capture_output=True, text=True).stdout,
        "dns_servers": subprocess.run(["cat", "/etc/resolv.conf"], capture_output=True, text=True).stdout,
        "firewall_rules": subprocess.run(["iptables", "-L"], capture_output=True, text=True).stdout
    }
