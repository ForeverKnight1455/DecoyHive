import platform
import subprocess
import json
import os
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

def get_installed_software_windows():
    """Get a list of installed software on Windows using the registry."""
    try:
        import winreg
        software_list = []
        keys = [
            r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall",
            r"SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall"
        ]

        for key in keys:
            with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, key) as reg_key:
                for i in range(winreg.QueryInfoKey(reg_key)[0]):
                    try:
                        subkey_name = winreg.EnumKey(reg_key, i)
                        with winreg.OpenKey(reg_key, subkey_name) as subkey:
                            name, _ = winreg.QueryValueEx(subkey, "DisplayName")
                            software_list.append(name)
                    except FileNotFoundError:
                        pass
                    except OSError:
                        pass

        return software_list
    except Exception as e:
        logging.error(f"Windows software detection failed: {str(e)}")
        return f"Error: {str(e)}"

def get_installed_software_debian():
    """Get a list of installed software on Debian-based systems using dpkg."""
    try:
        result = subprocess.run(['dpkg', '--list'], capture_output=True, text=True)
        software_list = [line.split()[1] for line in result.stdout.splitlines() if line.startswith("ii")]
        return software_list
    except Exception as e:
        logging.error(f"Debian-based software detection failed: {str(e)}")
        return f"Error: {str(e)}"

def get_installed_software_redhat():
    """Get a list of installed software on Red Hat-based systems using rpm."""
    try:
        result = subprocess.run(['rpm', '-qa'], capture_output=True, text=True)
        software_list = result.stdout.splitlines()
        return software_list
    except Exception as e:
        logging.error(f"Red Hat-based software detection failed: {str(e)}")
        return f"Error: {str(e)}"

def get_installed_software_arch():
    """Get a list of installed software on Arch-based systems using pacman."""
    try:
        result = subprocess.run(['pacman', '-Q'], capture_output=True, text=True)
        software_list = [line.split()[0] for line in result.stdout.splitlines()]
        return software_list
    except Exception as e:
        logging.error(f"Arch-based software detection failed: {str(e)}")
        return f"Error: {str(e)}"

def get_installed_software_gentoo():
    """Get a list of installed software on Gentoo-based systems using emerge."""
    try:
        result = subprocess.run(['equery', 'list', '*'], capture_output=True, text=True)
        software_list = [line.split()[0] for line in result.stdout.splitlines()]
        return software_list
    except Exception as e:
        logging.error(f"Gentoo-based software detection failed: {str(e)}")
        return f"Error: {str(e)}"

def get_installed_software_linux():
    """Get a list of installed software on Linux using the appropriate package manager."""
    results = {"debian": [], "rhl": [], "arch": [], "gentoo": []}

    try:
        if os.path.exists('/usr/bin/dpkg'):
            logging.info("Detecting Debian-based software...")
            results["debian"] = get_installed_software_debian()
        if os.path.exists('/bin/rpm'):
            logging.info("Detecting Red Hat-based software...")
            results["rhl"] = get_installed_software_redhat()
        if os.path.exists('/usr/bin/pacman'):
            logging.info("Detecting Arch-based software...")
            results["arch"] = get_installed_software_arch()
        if os.path.exists('/usr/bin/emerge'):
            logging.info("Detecting Gentoo-based software...")
            results["gentoo"] = get_installed_software_gentoo()

        # Determine the primary package manager based on results
        if results["debian"]:
            logging.info("Primary package manager: dpkg (Debian-based)")
        elif results["rhl"]:
            logging.info("Primary package manager: rpm (Red Hat-based)")
        elif results["arch"]:
            logging.info("Primary package manager: pacman (Arch-based)")
        elif results["gentoo"]:
            logging.info("Primary package manager: emerge (Gentoo-based)")
        else:
            logging.warning("No supported Linux package manager found.")
            return "Unsupported Linux distribution"

        return results


    except Exception as e:
        logging.error(f"Linux software detection failed: {str(e)}")
        return f"Error: {str(e)}"

def get_installed_software():
    """Detect OS and get installed software accordingly."""
    system = platform.system()
    if system == "Windows":
        logging.info("Detecting Windows software...")
        return get_installed_software_windows()
    elif system == "Linux":
        logging.info("Detecting Linux software...")
        return get_installed_software_linux()
    else:
        logging.warning("Unsupported OS detected.")
        return "Unsupported OS"

if __name__ == "__main__":
    software_list = get_installed_software()



    if isinstance(software_list, dict):
        print(json.dumps(software_list, indent=2))
    else:
        print(software_list)
