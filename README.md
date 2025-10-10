# Auto Create Ticket

This project is an automated ticket creation system.  
The setup, environment configuration, and service registration are handled via the provided `create_env.sh` script.

---

## 🚀 Features

- ✅ Automated environment setup using a single script  
- ✅ FastAPI-based REST API  
- ✅ Vector search using ChromaDB  
- ✅ Redis-powered chat memory  
- ✅ Logging, monitoring, and systemd service setup  
- ✅ Lightweight and easy to deploy  

---

## 🛠️ Tech Stack

- **Language**: Python 3.x  
- **Framework**: FastAPI  
- **Database**: ChromaDB  
- **Memory Store**: Redis  
- **Deployment**: Linux + Systemd  

---

## ⚙️ Installation & Setup

Run the installation script to set up the environment, install dependencies, and configure the service:

```bash
git clone https://github.com/monish8978/auto_create_ticket.git
cd auto_create_ticket
chmod +x create_env.sh
./create_env.sh


This script will:

🔧 Create a Python virtual environment

📦 Install all dependencies from requirements.txt

⚙️ Set up a systemd service at /etc/systemd/system/auto-create-ticket.service

🔁 Enable and start the auto-create-ticket service

✅ Verify that the service is active


▶️ Usage

Once setup is complete, the API will automatically start running as a service.

You can verify this by checking the status:

sudo systemctl status auto-create-ticket

It should show something like:

● auto-create-ticket.service - Auto Create Ticket FastAPI Service
   Active: active (running)


You can also manually start or stop the service anytime:

sudo systemctl restart auto-create-ticket
sudo systemctl stop auto-create-ticket


🌐 Accessing the API

Once the service is running, the FastAPI application will be accessible at:

http://<server-ip>:9003


If running locally:

http://0.0.0.0:9003


🧠 Note

Make sure Redis is installed and running on your system before starting the app.
If not installed, you can install it using:

sudo apt install redis -y


sudo systemctl enable redis
sudo systemctl start redis


🗓️ Crontab

The setup also ensures a cron job is added:

*/2 * * * * /Czentrix/apps/auto_create_ticket/venv/bin/python /Czentrix/apps/auto_create_ticket/service_check.py

This job runs every 2 minutes to check and manage services.

📁 Logs

Logs are stored at:

/var/log/czentrix/auto_create_ticket.log


You can monitor logs using:

tail -f /var/log/czentrix/auto_create_ticket.log
