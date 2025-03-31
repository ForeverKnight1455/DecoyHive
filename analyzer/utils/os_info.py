import platform
import subprocess

def get_os_info():
    """Collect operating system information."""
    os_type = platform.system()
    detected_distro = "Unknown"

    # if linux then get ID_LIKE value from /etc/os-release
    if os_type == "Linux":
        try:
            with open("/etc/os-release", "r") as f:
                for line in f:
                    if line.startswith("ID_LIKE="):
                        detected_distro = line.split("=")[1].strip().strip('"')
                        break
        except FileNotFoundError:
            detected_distro = "Unknown"


    return {
        "os_type": os_type,
        "os_version": f"{os_type.lower()} {platform.release()}",
        "os_architecture": platform.machine(),
        "kernel_version": platform.version(),
        "detected_distro" : detected_distro
    }
