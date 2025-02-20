import platform
import subprocess
import json
import os

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
        return f"Error: {str(e)}"

def get_installed_software_linux():
    """Get a list of installed software on Linux using dpkg or rpm."""
    try:
        if os.path.exists('/usr/bin/dpkg'):
            result = subprocess.run(['dpkg', '--list'], capture_output=True, text=True)
            software_list = [line.split()[1] for line in result.stdout.splitlines() if line.startswith("ii")]
        elif os.path.exists('/bin/rpm'):
            result = subprocess.run(['rpm', '-qa'], capture_output=True, text=True)
            software_list = result.stdout.splitlines()
        else:
            return "Unsupported Linux package manager"
        
        return software_list
    except Exception as e:
        return f"Error: {str(e)}"

def get_installed_software():
    """Detect OS and get installed software accordingly."""
    system = platform.system()
    if system == "Windows":
        return get_installed_software_windows()
    elif system == "Linux":
        return get_installed_software_linux()
    else:
        return "Unsupported OS"

if __name__ == "__main__":
    software_list = get_installed_software()
    
    # Print software list
    if isinstance(software_list, list):
        print(json.dumps(software_list, indent=2))
    else:
        print(software_list)
