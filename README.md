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

