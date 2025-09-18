# URL of the Hugging Face inference server
# This is the endpoint where text embedding requests will be sent.
OLLAMA_URL = "https://api-embeddings-ollama.c-zentrix.com/api/embeddings"

BITNET_URL = "https://api-retriever-bitnet.c-zentrix.com/v1/completions"

# Name of the model to use for text embeddings
# This should match the model available on your HF inference server.
OLLAMA_MODEL_NAME = "nomic-embed-text:v1.5"

BITNET_MODEL_NAME = "BitNet-b1.58-2B-4T"

# Port on which your FastAPI (or other service) will run
PORT = 9003

# Directory where log files will be stored
# Make sure this path exists and has write permissions.
LOG_DIR = "/var/log/czeentrix/"

# Name of the log file for this application
LOG_FILENAME = "auto_create_ticket.log"

# Redis connection URL
# Used for caching, storing temporary data, or managing message queues.
REDIS_URL = "redis://localhost:6379"
