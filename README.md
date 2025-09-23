# Auto Create Ticket

This project is an automated ticket creation system.  
The setup and environment creation are handled via the provided `.sh` script.

---

## 🚀 Features
- Automated environment setup using a single script  
- Ticket creation and management system  
- Logging and monitoring included  
- Lightweight and easy to run  

---

## 🛠️ Tech Stack
- **Language**: Python 3.x  
- **Framework**: FastAPI  
- **Database**: ChromaDB  
- **Deployment**: Linux, Git  

---


---

## ⚙️ Installation & Setup

Run the installation script to set up the environment and install dependencies:

```bash
git clone https://github.com/monish8978/auto_create_ticket.git
cd auto_create_ticket
chmod +x create_env.sh
./create_env.sh
source venv/bin/activate

This script will:

Create a Python virtual environment

Activate the environment

Install required dependencies from requirements.txt

Setup initial configuration


## ▶️ Usage

Start the application:

python app.py

Or with Uvicorn (if FastAPI is used):

uvicorn app:app --host 0.0.0.0 --port 9003

Access the app at 👉 http://localhost:9003

⚙️ Systemd Service Setup

To run the app as a service that starts on boot and restarts automatically, create a systemd service file:

1. Create file /etc/systemd/system/auto_create_ticket.service with the following content:

[Unit]
Description=Auto Create Ticket FastAPI Service
After=network.target

[Service]
WorkingDirectory=/Czentrix/apps/auto_create_ticket
ExecStart=/Czentrix/apps/auto_create_ticket/venv/bin/uvicorn app:app --host 0.0.0.0 --port 9003 --workers 4
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target


2. Reload systemd to register the new service:

sudo systemctl daemon-reload

3. Enable and start the service:

sudo systemctl enable auto_create_ticket
sudo systemctl start auto_create_ticket

4. Check service status:

sudo systemctl status auto_create_ticket



