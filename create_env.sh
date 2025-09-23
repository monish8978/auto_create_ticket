#!/bin/bash

# Setting up the directory
cd /Czentrix/apps/auto_create_ticket/
cdir="$(pwd)/venv/bin/"

# Printing the directory for debugging
echo "Virtual environment directory: $cdir"

# Creating virtual environment
echo "Creating virtual environment..."
python3 -m venv venv
virtualenv venv -p /opt/python3.6.7/bin/python3
echo "Virtual environment created."

# Activating the virtual environment
source venv/bin/activate

# Installing requirements
echo "Installing requirements..."
pip install -r requirements.txt
echo "Requirements installed."


# -----------------------------
# Systemd Service Setup
# -----------------------------

SERVICE_DIR="/etc/systemd/system"
SERVICE_FILE="$SERVICE_DIR/auto_create_ticket.service"

# 1️⃣ Ensure /etc/systemd/system directory exists
if [ ! -d "$SERVICE_DIR" ]; then
    echo "Creating systemd directory: $SERVICE_DIR"
    sudo mkdir -p "$SERVICE_DIR"
else
    echo "Systemd directory already exists: $SERVICE_DIR"
fi

# 2️⃣ Check if service file already exists
if [ -f "$SERVICE_FILE" ]; then
    echo "Service file already exists at $SERVICE_FILE — skipping creation."
else
    echo "Creating systemd service file at $SERVICE_FILE..."
    
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

    # Set permissions
    sudo chmod 644 "$SERVICE_FILE"

    # Reload and start service
    echo "Reloading systemd..."
    sudo systemctl daemon-reload

    echo "Enabling and starting auto_create_ticket service..."
    sudo systemctl enable auto_create_ticket
    sudo systemctl start auto_create_ticket
fi


# -----------------------------
# Add Crontab Entry (Service Health Check)
# -----------------------------

CRON_JOB="*/2 * * * * /Czentrix/apps/auto_create_ticket/venv/bin/python /Czentrix/apps/auto_create_ticket/service_check.py"

# Check if cron job already exists
(crontab -l 2>/dev/null | grep -F "$CRON_JOB") >/dev/null

if [ $? -eq 0 ]; then
    echo "Crontab entry already exists — skipping."
else
    echo "Adding crontab entry..."
    # Append the new cron job
    (crontab -l 2>/dev/null; echo "$CRON_JOB") | crontab -
    echo "Crontab entry added."
fi
