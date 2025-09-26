from settings import SERVICE_FILE
from utils.logger import log
import subprocess
import gc
from concurrent.futures import ThreadPoolExecutor

def is_service_active(service_name):
    """Check if the service is active on the system."""
    try:
        # Run the systemctl command to check if the service is active
        result = subprocess.run(
            ['systemctl', 'is-active', service_name],  # Command to check if the service is active
            stdout=subprocess.PIPE,  # Capture the standard output (service status)
            stderr=subprocess.PIPE,  # Capture any error messages
            universal_newlines=True  # Convert byte output to string
        )

        # Log service status: If the output is 'active', log that the service is active, else it's not active
        if result.stdout.strip() == 'active':
            log.info(f"Service '{service_name}' is already active.")
            return True  # Service is active
        else:
            log.info(f"Service '{service_name}' is not active.")
            return False  # Service is not active
    except Exception as e:
        # If an error occurs while checking service status, log it
        log.error(f"Error while checking service status for {service_name}: {e}")
        return False  # Return False as the service check failed

def start_service(service_name):
    """Start the service if it's not active."""
    try:
        # Run the systemctl command to start the service
        subprocess.run(['sudo', 'systemctl', 'restart', service_name], check=True)  # Use check=True to raise an error if the command fails
        log.info(f"Service '{service_name}' has been started.")  # Log success message when the service is started
    except subprocess.CalledProcessError as e:
        # If starting the service fails, log the error
        log.error(f"Error starting service '{service_name}': {e}")
    except Exception as e:
        # If there is any other error, log it
        log.error(f"Unexpected error while starting service '{service_name}': {e}")

def manage_service(service_name):
    """Check if the service is active and start it if necessary, and handle cleanup."""
    if not is_service_active(service_name):  # If the service is not active
        start_service(service_name)  # Start the service

def garbage_collect():
    """Manually run garbage collection to manage memory usage."""
    gc.collect()  # Trigger the garbage collector to free up unused memory

def run_in_threads(services):
    """Run service management in multiple threads."""
    with ThreadPoolExecutor() as executor:
        # Executor maps the `manage_service` function to each service in the list, running them in parallel threads
        executor.map(manage_service, services)

    # Perform garbage collection after the tasks are completed
    garbage_collect()

if __name__ == "__main__":
    # List of services to manage (this can be expanded to include multiple services)
    services_to_manage = [SERVICE_FILE]  # Example service list

    # Run the service management for each service in parallel using threads
    run_in_threads(services_to_manage)


