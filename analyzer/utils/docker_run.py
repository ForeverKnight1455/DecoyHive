import subprocess
import os
import time
import signal
import sys

def container_exists(container_name):
    """Check if a container with the given name already exists."""
    try:
        result = subprocess.run(
            ["docker", "ps", "-a", "--filter", f"name={container_name}", "--format", "{{.Names}}"],
            stdout=subprocess.PIPE,
            text=True
        )
        return container_name in result.stdout.strip().split("\n")
    except subprocess.CalledProcessError as e:
        print(f"Error checking container existence: {e}")
        return False

def image_exists(image_name):
    """Check if a Docker image with the given name already exists."""
    try:
        result = subprocess.run(
            ["docker", "images", "--filter", f"reference={image_name}", "--format", "{{.Repository}}"],
            stdout=subprocess.PIPE,
            text=True
        )
        return image_name in result.stdout.strip().split("\n")
    except subprocess.CalledProcessError as e:
        print(f"Error checking image existence: {e}")
        return False

def get_container_identifier(container_name):
    """Return the container name or ID for use in configurations."""
    return container_name

def build_and_run_docker():
    dockerfile_path = "./output/Dockerfile"
    image_name = "collected_data_image"
    container_name = "honeypot_container"

    if not os.path.exists(dockerfile_path):
        print("Error: Dockerfile not found! Ensure it is generated first.")
        sys.exit(1)

    try:
        # Check if the image already exists
        if not image_exists(image_name):
            print("Building Docker image...")
            subprocess.run([
                "docker", "build", "-t", image_name, "-f", dockerfile_path, "./output"
            ], check=True)
        else:
            print(f"Docker image '{image_name}' already exists. Reusing it.")

        # Check if the container already exists
        if not container_exists(container_name):
            print("Running Docker container with port mappings...")
            subprocess.run([
                "docker", "run", "--name", container_name,
                "--cap-add=NET_ADMIN",
                "-p", "22:22",  # Map host port 22 to container port 22
                "-p", "80:80",  # Map host port 80 to container port 80
                "-p", "443:443",  # Map host port 443 to container port 443
                "-d",
                image_name
            ], check=True)
            print(f"Container '{container_name}' is running.")
        else:
            print(f"Container '{container_name}' already exists. Reusing it.")

        # Return container name as the identifier
        return container_name
    except subprocess.CalledProcessError as e:
        print(f"Error: {e}")
        print("Ensure Docker is installed and running.")
        sys.exit(1)

def stop_container(container_name, image_name):
    try:
        print(f"Stopping container '{container_name}'...")
        subprocess.run(["docker", "stop", container_name], check=True)
        subprocess.run(["docker", "rm", container_name], check=True)
        print(f"Container '{container_name}' has been stopped and removed.")
    except subprocess.CalledProcessError as e:
        print(f"Error stopping/removing container: {e}")

    print(f"Deleting Docker image '{image_name}'...")
    try:
        subprocess.run(["docker", "rmi", image_name], check=True)
        print(f"Image '{image_name}' has been deleted.")
    except subprocess.CalledProcessError as e:
        print(f"Error deleting image: {e}")

def main():
    container_name = build_and_run_docker()

    def signal_handler(sig, frame):
        print("\nExiting script; cleaning up...")
        stop_container(container_name, "collected_data_image")
        sys.exit(0)

    # Register signal handlers for graceful exit
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    print("Script running continuously. Press Ctrl+C to exit.")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        signal_handler(None, None)

if __name__ == "__main__":
    main()
