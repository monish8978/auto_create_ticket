# ==========================
# 🔧 Configuration Settings
# ==========================
# This file contains all the environment and service configurations 
# required for running the Auto Create Ticket application.

# --------------------------
# Hugging Face / Ollama APIs
# --------------------------

# URL of the Ollama-based Hugging Face inference server
# 👉 This is the API endpoint used to generate text embeddings.
# Example: Convert a text/document into vector form for semantic search.
OLLAMA_URL = "https://api-embeddings-ollama.c-zentrix.com/api/embeddings"

# Model name for generating embeddings
# 👉 Ensure this matches a valid model available on the inference server.
OLLAMA_MODEL_NAME = "nomic-embed-text:v1.5"


# --------------------------
# BitNet Retriever API
# --------------------------

# URL for the BitNet retriever model
# 👉 Used for text generation / retrieval tasks.
BITNET_URL = "https://api-embeddings-ollama.c-zentrix.com/api/chat"

# Model name for the BitNet retriever
BITNET_MODEL_NAME = "mistral:latest"


# --------------------------
# FastAPI Service Settings
# --------------------------

# Port on which the FastAPI service will run
# 👉 Default: 9003
PORT = 9003


# --------------------------
# Logging Configuration
# --------------------------

# Directory where log files will be stored
# 👉 Make sure this directory exists and has write permissions
LOG_DIR = "/var/log/czeentrix/"

# Name of the log file used for this application
LOG_FILENAME = "auto_create_ticket.log"


# --------------------------
# Redis Configuration
# --------------------------

# Redis connection URL
# 👉 Used for:
#    - Caching
#    - Storing chat history
#    - Managing session context
REDIS_URL = "redis://localhost:6379"
