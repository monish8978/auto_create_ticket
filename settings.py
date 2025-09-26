# ==========================
# 🔧 Configuration Settings
# ==========================
# This file contains all the environment and service configurations 
# required for running the Auto Create Ticket application.

# --------------------------
# Hugging Face / Ollama APIs
# --------------------------

# ✅ OLLAMA_URL:
# This is the endpoint for the Ollama server that provides text embeddings.
# Embeddings convert text into numerical vectors for similarity search.
# These vectors are later stored in ChromaDB for retrieval.
OLLAMA_URL = "https://api-embeddings-ollama.c-zentrix.com/api/embeddings"

# ✅ OLLAMA_MODEL_NAME:
# This is the specific embedding model to use on the Ollama server.
# Make sure this model is deployed and available on the endpoint.
OLLAMA_MODEL_NAME = "nomic-embed-text:v1.5"


# --------------------------
# BitNet Retriever API
# --------------------------

# ✅ BITNET_URL:
# This API is used for **generating responses** based on retrieved content.
# It's typically backed by a large language model (LLM) like Mistral.
BITNET_URL = "https://api-embeddings-ollama.c-zentrix.com/api/chat"

# ✅ BITNET_MODEL_NAME:
# This is the specific model used for generating human-like responses.
# It works with the /chat endpoint to answer user queries.
BITNET_MODEL_NAME = "mistral:latest"


# --------------------------
# FastAPI Service Settings
# --------------------------

# ✅ PORT:
# The port on which your FastAPI app will be served.
# Default is 9003, but you can change it if the port is already in use.
PORT = 9003


# --------------------------
# Logging Configuration
# --------------------------

# ✅ LOG_DIR:
# This is the directory where log files will be stored.
# Make sure this directory exists and is writable by the service.
LOG_DIR = "/var/log/czentrix/"

# ✅ LOG_FILENAME:
# Name of the log file for your FastAPI app.
# Log files help in debugging, monitoring, and auditing.
LOG_FILENAME = "auto_create_ticket.log"


# --------------------------
# Redis Configuration
# --------------------------

# ✅ REDIS_URL:
# Redis is used for:
#   - Storing session-based chat history (via RedisChatMessageHistory)
#   - Cache mechanisms (optional)
# Format: redis://<host>:<port>
REDIS_URL = "redis://127.0.0.1:6379"


# --------------------------
# Systemd Service Name
# --------------------------

# ✅ SERVICE_FILE:
# This is the name of the systemd service file, used when managing the app with:
#   - `systemctl status auto-create-ticket`
#   - `systemctl start auto-create-ticket`
SERVICE_FILE = "auto-create-ticket"

