# ==========================
# 🔧 Configuration Settings
# ==========================
# This file centralizes all environment variables and service configurations
# required to run the Auto Create Ticket application.
# It includes API endpoints, model names, ports, logging, Redis settings, and AI credentials.


# --------------------------
# Hugging Face / Ollama APIs
# --------------------------
# Used for generating **text embeddings**, which are numerical vector representations of text.
# Embeddings enable semantic similarity searches, useful for retrieving relevant documents.

# ✅ OLLAMA_URL:
# Endpoint for the Ollama server that generates embeddings.
# The application sends POST requests with text and receives vector embeddings in response.
OLLAMA_URL = "https://api-embeddings-ollama.c-zentrix.com/api/embeddings"

# ✅ OLLAMA_MODEL_NAME:
# Specific embedding model deployed on Ollama.
# Ensure this model is active at the endpoint. Different models may produce slightly different embeddings.
OLLAMA_MODEL_NAME = "nomic-embed-text:v1.5"


# --------------------------
# BitNet Retriever API
# --------------------------
# Used for generating **human-like responses** based on retrieved documents from ChromaDB.
# Essentially, this is the LLM endpoint for answering user queries.

# ✅ BITNET_URL:
# Endpoint for the chat or LLM service.
# The app sends context and user queries here to generate responses.
BITNET_URL = "https://api-embeddings-ollama.c-zentrix.com/api/chat"

# ✅ BITNET_MODEL_NAME:
# Name of the LLM used for generating responses.
# Must match a deployed model at the chat endpoint (e.g., Mistral latest version).
BITNET_MODEL_NAME = "mistral:latest"


# --------------------------
# FastAPI Service Settings
# --------------------------
# Settings for running the FastAPI server.

# ✅ PORT:
# Port on which the FastAPI application will run.
# Default is 9003; change only if another service uses this port.
PORT = 9003


# --------------------------
# Logging Configuration
# --------------------------
# Determines where logs are stored and their file naming.

# ✅ LOG_DIR:
# Directory to save application logs.
# Must exist and be writable by the FastAPI service.
LOG_DIR = "/var/log/czentrix/"

# ✅ LOG_FILENAME:
# Name of the log file for the FastAPI application.
# Useful for debugging, monitoring, and auditing application behavior.
LOG_FILENAME = "auto_create_ticket.log"


# --------------------------
# Redis Configuration
# --------------------------
# Redis is used for storing session-based chat history and optional caching.

# ✅ REDIS_URL:
# URL for connecting to the Redis server.
# Format: redis://<host>:<port>
# The application uses this to persist chat sessions and maintain state between requests.
REDIS_URL = "redis://127.0.0.1:6379"


# --------------------------
# Systemd Service Name
# --------------------------
# Name of the systemd service for managing the app as a background service.

# ✅ SERVICE_FILE:
# Name of the service file for systemd.
# Commands you can run:
#   systemctl status auto-create-ticket   # Check status
#   systemctl start auto-create-ticket    # Start service
#   systemctl restart auto-create-ticket  # Restart service
SERVICE_FILE = "auto-create-ticket"


# --------------------------
# Groq API Settings
# --------------------------
# Used to authenticate and configure access to Groq AI services.

# ✅ GROQ_API_KEY:
# API key for authenticating requests to Groq.
# Keep this key secure, as it grants access to the AI model.
GROQ_API_KEY = ""

# ✅ GROQ_MODEL:
# Specific Groq model to use for generating AI responses.
# Example: LLaMA 3.1 8B Instant for fast, interactive responses.
GROQ_MODEL = "llama-3.1-8b-instant"
