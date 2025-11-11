# ===========================================
# 🛠 Service Manager Script
# ===========================================
# This script checks whether a systemd service is active.
# If the service is inactive, it will attempt to start or restart it.
# It supports managing multiple services in parallel using threads.
# Additionally, it performs garbage collection after operations to free memory.

from settings import SERVICE_FILE  # Import the service name from settings
from utils.logger import log        # Custom logger for logging info and errors
import subprocess                  # Allows running shell commands like systemctl
import gc                           # Garbage collection to free unused memory
from concurrent.futures import ThreadPoolExecutor  # ThreadPool for parallel execution


def is_service_active(service_name):
    """
    Check if a systemd service is active on the system.

    Args:
        service_name (str): The name of the service to check.

    Returns:
        bool: True if the service is active, False otherwise.
    """
    try:
        # Run `systemctl is-active <service>` to check service status
        result = subprocess.run(
            ['systemctl', 'is-active', service_name],  # System command
            stdout=subprocess.PIPE,  # Capture output
            stderr=subprocess.PIPE,  # Capture errors
            universal_newlines=True  # Decode bytes to string
        )

        # Strip any whitespace/newlines and check the output
        if result.stdout.strip() == 'active':
            log.info(f"Service '{service_name}' is already active.")  # Log active status
            return True
        else:
            log.info(f"Service '{service_name}' is not active.")  # Log inactive status
            return False
    except Exception as e:
        # Catch any exceptions and log them
        log.error(f"Error while checking service status for {service_name}: {e}")
        return False  # Return False if check fails


def start_service(service_name):
    """
    Start or restart a systemd service if it's inactive.

    Args:
        service_name (str): The name of the service to start/restart.
    """
    try:
        # Use `sudo systemctl restart <service>` to ensure the service runs
        subprocess.run(['sudo', 'systemctl', 'restart', service_name], check=True)
        log.info(f"Service '{service_name}' has been started.")  # Log successful start
    except subprocess.CalledProcessError as e:
        # Raised if the systemctl command fails
        log.error(f"Error starting service '{service_name}': {e}")
    except Exception as e:
        # Catch any other unexpected errors
        log.error(f"Unexpected error while starting service '{service_name}': {e}")


def manage_service(service_name):
    """
    Check service status and start it if inactive.
    Also serves as a wrapper for threading execution.

    Args:
        service_name (str): Name of the service to manage.
    """
    if not is_service_active(service_name):  # Check service
        start_service(service_name)  # Start it if not active


def garbage_collect():
    """
    Perform manual garbage collection to free unused memory.
    Useful after running multiple threads/tasks to clean up resources.
    """
    gc.collect()
    log.info("Garbage collection completed.")


def run_in_threads(services):
    """
    Run service management for multiple services in parallel threads.

    Args:
        services (list): List of service names to manage.
    """
    # Create a ThreadPoolExecutor to run tasks concurrently
    with ThreadPoolExecutor() as executor:
        # Map the `manage_service` function to each service in the list
        executor.map(manage_service, services)

    # Run garbage collection after all threads are finished
    garbage_collect()


if __name__ == "__main__":
    # List of services to manage; can add multiple services here
    services_to_manage = [SERVICE_FILE]

    # Start the threaded service management
    run_in_threads(services_to_manage)
