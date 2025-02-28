import psutil
import platform
import random
import subprocess

def get_hardware_info():
    """Collect hardware information with some randomized elements."""
    def randomize_size(size_gb):
        return f"{size_gb * random.uniform(0.8, 1.2):.2f} GB"

    def randomize_mac(original_mac):
        if original_mac == "N/A" or len(original_mac.split(':')) != 6:
            return original_mac
        mac_parts = original_mac.split(':')
        randomized_mac = mac_parts[:3] + [f"{random.randint(0, 255):02x}" for _ in range(3)]
        return ':'.join(randomized_mac)

    def get_essential_cpu_flags():
        essential_flags = {"sse", "sse2", "sse4_1", "sse4_2", "avx", "avx2", "aes", "fma", "pclmulqdq", "popcnt"}
        try:
            result = subprocess.run(["lscpu"], capture_output=True, text=True)
            for line in result.stdout.split("\n"):
                if "Flags:" in line:
                    return [flag for flag in line.split(":")[1].strip().split() if flag in essential_flags]
        except Exception:
            return []
        return []

    cpu_info = {
        "model": platform.processor(),
        "architecture": platform.machine(),
        "cores": psutil.cpu_count(logical=False),
        "threads": psutil.cpu_count(logical=True),
        "frequency": f"{psutil.cpu_freq().max:.2f} MHz",
        "flags": get_essential_cpu_flags()
    }

    memory_info = {
        "total": f"{psutil.virtual_memory().total / (1024 ** 3):.2f} GB",
        "available": f"{psutil.virtual_memory().available / (1024 ** 3):.2f} GB"
    }

    disk_info = {
        "total": randomize_size(psutil.disk_usage('/').total / (1024 ** 3)),
        "partitions": [
            {
                "device": part.device,
                "mountpoint": part.mountpoint,
                "fstype": part.fstype,
                "total_size": randomize_size(psutil.disk_usage(part.mountpoint).total / (1024 ** 3))
            }
            for part in psutil.disk_partitions()
        ]
    }

    network_info = [
        {
            "name": name,
            "ip": addr.address,
            "mac": randomize_mac(addr.address) if addr.family == psutil.AF_LINK else "N/A"
        }
        for name, addrs in psutil.net_if_addrs().items()
        for addr in addrs
    ]

    return {
        "cpu": cpu_info,
        "memory": memory_info,
        "disk": disk_info,
        "network_interfaces": network_info
    }

if __name__ == "__main__":
    import json
    print(json.dumps(get_hardware_info(), indent=4))
