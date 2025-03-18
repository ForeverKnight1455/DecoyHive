import platform
import subprocess

def get_os_info():
    """Collect operating system information."""
    os_type = platform.system()
    return {
        "os_type": os_type,
        "os_version": f"{os_type.lower()} {platform.release()}",
        "os_architecture": platform.machine(),
        "kernel_version": platform.version(),
    }
