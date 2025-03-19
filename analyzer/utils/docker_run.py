import subprocess
import os
import time
import signal
import sys

def build_and_run_docker():
    dockerfile_path = "Dockerfile"
    image_name = "collected_data_image"
    container_name = "collected_data_container"

    if not os.path.exists(dockerfile_path):
        print("Error: Dockerfile not found! Ensure it is generated first.")
        sys.exit(1)

    try:
        print("Building Docker image...")
        subprocess.run(["docker", "build", "-t", image_name, "."], check=True)

        print("Running Docker container...")
        subprocess.run([
            "docker", "run", 
            "--name", container_name, 
            "--cap-add=NET_ADMIN", 
            "-d", 
            image_name
        ], check=True)
        print(f"Container '{container_name}' is running.")
        return container_name
    except subprocess.CalledProcessError as e:
        print(f"Error: {e}")
        print("Ensure Docker is installed and running.")
        sys.exit(1)

def stop_container(container_name):
    try:
        print(f"Stopping container '{container_name}'...")
        subprocess.run(["docker", "stop", container_name], check=True)
        subprocess.run(["docker", "rm", container_name], check=True)
        print(f"Container '{container_name}' has been stopped and removed.")
    except subprocess.CalledProcessError as e:
        print(f"Error stopping/removing container: {e}")

def main():
    container_name = build_and_run_docker()

    def signal_handler(sig, frame):
        print("\nExiting script; cleaning up container...")
        stop_container(container_name)
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
