import psutil
import platform

def get_hardware_info():
    """Collect hardware information."""
    return {
        "cpu": platform.processor(),
        "cpu_cores": psutil.cpu_count(logical=False),
        "cpu_threads": psutil.cpu_count(logical=True),
        "memory": f"{psutil.virtual_memory().total / (1024 ** 3):.2f} GB",
        "disk": f"{psutil.disk_usage('/').total / (1024 ** 3):.2f} GB",
        "network_interfaces": [
            {
                "name": name,
                "ip": addr.address,
                "mac": addr.address if addr.family == psutil.AF_LINK else "N/A"
            }
            for name, addrs in psutil.net_if_addrs().items()
            for addr in addrs
        ]
    }
