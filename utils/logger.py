import logging
from logging.handlers import TimedRotatingFileHandler
import os
from settings import LOG_DIR, LOG_FILENAME

# Ensure log directory exists (create if not present)
os.makedirs(LOG_DIR, exist_ok=True)

# Full log file path (e.g., /var/log/czentrix/auto_create_ticket.log)
LOG_FILE = os.path.join(LOG_DIR, LOG_FILENAME)

# Create main logger instance for the app
log = logging.getLogger("auto_create_ticket")
log.setLevel(logging.INFO)  # Default logging level (INFO and above)

# Define log format
# Example output: 2025-09-18 13:20:15,123 - auto_create_ticket - INFO - 42 - Starting app...
formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(lineno)d - %(message)s'
)

# ------------------------------
# File Handler (rotating logs)
# ------------------------------
# - Creates daily log file (rotates at midnight)
# - Keeps 7 days backup logs
# - Stores logs in LOG_FILE path
file_handler = TimedRotatingFileHandler(
    LOG_FILE, when="midnight", interval=1, backupCount=7, encoding="utf-8"
)
file_handler.setFormatter(formatter)  # Apply formatter
file_handler.setLevel(logging.INFO)   # Log only INFO and above

# ------------------------------
# Console Handler (stdout logs)
# ------------------------------
# - Prints logs to console (useful for dev / debugging)
console_handler = logging.StreamHandler()
console_handler.setFormatter(formatter)  # Apply formatter
console_handler.setLevel(logging.INFO)   # Log only INFO and above

# ------------------------------
# Attach Handlers
# ------------------------------
# Prevents duplicate log entries if logger is imported multiple times
if not log.handlers:
    log.addHandler(file_handler)
    log.addHandler(console_handler)

# Now, you can log messages like:
# log.info("App started successfully")
# log.error("Something went wrong", exc_info=True)
