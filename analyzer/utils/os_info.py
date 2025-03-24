import platform
import subprocess

def get_os_info():
    """Collect operating system information."""
    os_type = platform.system()
    if(os_type == "Windows"):
        return {
            "os_type": os_type,
            "os_version": f"{os_type} {platform.version()}",
            "os_architecture": platform.architecture()[0],
            "kernel_version": platform.version(),
        }
    elif(os_type == "Linux"):
        return {
            "os_type": os_type,
            "os_version": f"{os_type.lower()} {platform.release()}",
            "os_architecture": platform.machine(),
            "kernel_version": platform.version(),
        }
