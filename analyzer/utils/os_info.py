import platform
import subprocess

def get_os_info():
    """Collect operating system information."""
    return {
        "os_type": platform.system(),
        "os_version": platform.release(),
        "os_architecture": platform.machine(),
        "kernel_version": platform.version(),
        "installed_packages": subprocess.run(["dpkg", "-l"], capture_output=True, text=True).stdout
    }
