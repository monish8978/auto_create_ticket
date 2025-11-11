#!/bin/bash

# ================================
# 🚀 Auto Create Ticket Setup Script
# ================================
# This script sets up the Auto Create Ticket FastAPI application, including:
# 1. Python virtual environment setup
# 2. Installing dependencies
# 3. Configuring a systemd service
# 4. Adding a cron job for health checks
# ================================

# -------------------------------
# 1️⃣ Navigate to application directory
# -------------------------------
cd /Czentrix/apps/auto_create_ticket/
# Store the path to the virtual environment's bin directory
cdir="$(pwd)/venv/bin/"

# Print the directory path for debugging
echo "Virtual environment directory: $cdir"

# -------------------------------
# 2️⃣ Create Python Virtual Environment
# -------------------------------
echo "Creating virtual environment..."
# Create virtual environment using python3 default
python3 -m venv venv
# Optional: Create virtual environment with specific Python version
virtualenv venv -p /opt/python3.6.7/bin/python3
echo "Virtual environment created."

# Activate the virtual environment
source venv/bin/activate

# -------------------------------
# 3️⃣ Install Required Python Packages
# -------------------------------
echo "Installing requirements..."
# Install packages listed in requirements.txt
pip install -r requirements.txt
echo "Requirements installed."

# -------------------------------
# 4️⃣ Systemd Service Setup
# -------------------------------
SERVICE_DIR="/etc/systemd/system"
SERVICE_FILE="$SERVICE_DIR/auto-create-ticket.service"

# Ensure systemd service directory exists
if [ ! -d "$SERVICE_DIR" ]; then
    echo "Creating systemd directory: $SERVICE_DIR"
    sudo mkdir -p "$SERVICE_DIR"
else
    echo "Systemd directory already exists: $SERVICE_DIR"
fi

# Check if the service file already exists
if [ -f "$SERVICE_FILE" ]; then
    echo "Service file already exists at $SERVICE_FILE — skipping creation."
else
    echo "Creating systemd service file at $SERVICE_FILE..."
    
    # Create systemd service file for the FastAPI app
    sudo tee "$SERVICE_FILE" > /dev/null <<EOL
[Unit]
Description=Auto Create Ticket FastAPI Service
After=network.target

[Service]
WorkingDirectory=/Czentrix/apps/auto_create_ticket
ExecStart=$cdir/uvicorn app:app --host 0.0.0.0 --port 9003 --workers 4
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
EOL

    # Set proper permissions for the service file
    sudo chmod 644 "$SERVICE_FILE"

    # Reload systemd manager configuration
    echo "Reloading systemd..."
    sudo systemctl daemon-reload

    # Enable and start the service
    echo "Enabling and starting auto-create-ticket service..."
    sudo systemctl enable auto-create-ticket
    sudo systemctl restart auto-create-ticket
fi

# -------------------------------
# 5️⃣ Add Cron Job for Service Health Check
# -------------------------------
# Run the service_check.py script every 2 minutes to monitor service health
CRON_JOB="*/2 * * * * /Czentrix/apps/auto_create_ticket/venv/bin/python /Czentrix/apps/auto_create_ticket/service_check.py"

# Check if the cron job already exists
(crontab -l 2>/dev/null | grep -F "$CRON_JOB") >/dev/null

if [ $? -eq 0 ]; then
    echo "Crontab entry already exists — skipping."
else
    echo "Adding crontab entry..."
    # Append the cron job without overwriting existing entries
    (crontab -l 2>/dev/null; echo "$CRON_JOB") | crontab -
    echo "Crontab entry added."
fi
