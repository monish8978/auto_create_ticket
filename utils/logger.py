import logging
from logging.handlers import TimedRotatingFileHandler
import os
from settings import LOG_DIR, LOG_FILENAME

# ------------------------------
# Ensure log directory exists
# ------------------------------
# - If LOG_DIR does not exist, create it.
# - Ensures that the log files can be written without errors.
os.makedirs(LOG_DIR, exist_ok=True)

# Full log file path
# Example: /var/log/czentrix/auto_create_ticket.log
LOG_FILE = os.path.join(LOG_DIR, LOG_FILENAME)

# ------------------------------
# Create main logger
# ------------------------------
# - Name the logger "auto_create_ticket" to distinguish logs if multiple loggers exist.
# - Set default logging level to INFO (will capture INFO, WARNING, ERROR, CRITICAL).
log = logging.getLogger("auto_create_ticket")
log.setLevel(logging.INFO)

# ------------------------------
# Define log format
# ------------------------------
# Format: timestamp - logger name - level - line number - message
# Example: 2025-09-18 13:20:15,123 - auto_create_ticket - INFO - 42 - Starting app...
formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(lineno)d - %(message)s'
)

# ------------------------------
# File Handler (Rotating Logs)
# ------------------------------
# - Writes logs to a file.
# - Rotates daily at midnight.
# - Keeps 7 backup files (old logs are kept for 7 days).
# - Encoding set to UTF-8 to support all characters.
file_handler = TimedRotatingFileHandler(
    LOG_FILE, when="midnight", interval=1, backupCount=7, encoding="utf-8"
)
file_handler.setFormatter(formatter)  # Apply formatter to file logs
file_handler.setLevel(logging.INFO)   # Only log INFO and above to file

# ------------------------------
# Console Handler (stdout logs)
# ------------------------------
# - Prints logs to the console.
# - Useful during development or debugging to see logs in real time.
console_handler = logging.StreamHandler()
console_handler.setFormatter(formatter)  # Apply formatter to console logs
console_handler.setLevel(logging.INFO)   # Only log INFO and above to console

# ------------------------------
# Attach handlers to the logger
# ------------------------------
# - Prevent duplicate logs if this module is imported multiple times.
if not log.handlers:
    log.addHandler(file_handler)
    log.addHandler(console_handler)

# ------------------------------
# Usage Examples
# ------------------------------
# log.info("App started successfully")
# log.warning("This is a warning")
# log.error("An error occurred", exc_info=True)
