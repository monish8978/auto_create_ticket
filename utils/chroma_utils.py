import chromadb
from settings import OLLAMA_URL, OLLAMA_MODEL_NAME 
from chromadb.config import Settings
from langchain_text_splitters import RecursiveCharacterTextSplitter
import httpx
from typing import List
import traceback
from langchain_core.documents import Document
from utils.logger import log
import warnings

# -------------------------------
# Suppress unnecessary warnings
# -------------------------------
warnings.filterwarnings('ignore')


# -------------------------------
# Function: split_text
# -------------------------------
def split_text(text: str) -> List[Document]:
    """
    Splits input text into smaller chunks for embeddings.
    
    - Uses RecursiveCharacterTextSplitter from LangChain.
    - chunk_size=1000: maximum characters per chunk.
    - chunk_overlap=200: overlap to maintain context between chunks.
    - Returns a list of Document objects, each containing a chunk.
    """
    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    chunks = splitter.create_documents([text])
    return chunks


# -------------------------------
# Function: get_embeddings
# -------------------------------
async def get_embeddings(text: str):
    """
    Fetches embeddings from Ollama (via Hugging Face style API) for a given text.
    
    - Sends POST request with 'model' and 'prompt'.
    - Returns a list of vector embeddings.
    - Logs warning if embedding is empty.
    - Catches and logs any exceptions.
    """
    payload = {
        "model": OLLAMA_MODEL_NAME,
        "prompt": text   # Input text for embedding
    }

    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(OLLAMA_URL, json=payload)
            response.raise_for_status()  # Raise exception for HTTP errors
            data = response.json()
            vector = data.get("embedding", [])

            if vector == []:
                log.warning("Empty embedding vector received")

            return vector
    except Exception as e:
        log.error(f"Failed to fetch embedding: {e}", exc_info=True)
        return []


# -------------------------------
# Function: get_chroma_client
# -------------------------------
def get_chroma_client(path="./chroma_data_db"):
    """
    Initializes and returns a ChromaDB PersistentClient.
    
    - PersistentClient stores embeddings and metadata on disk.
    - 'anonymized_telemetry=False' disables sending anonymous usage data.
    - Default path is './chroma_data_db'.
    """
    return chromadb.PersistentClient(path=path, settings=Settings(anonymized_telemetry=False))


# -------------------------------
# Function: get_or_create_collection
# -------------------------------
def get_or_create_collection(client, name):
    """
    Retrieves an existing collection from ChromaDB.
    If it doesn't exist, creates a new one.
    
    - 'client': ChromaDB client instance.
    - 'name': Collection name.
    - Logs warning if collection creation is required.
    """
    try:
        return client.get_collection(name=name)
    except Exception as e:
        log.warning(f"Collection '{name}' not found. Creating new one. Error={e}")
        return client.create_collection(name=name)


# -------------------------------
# Function: add_chunks_to_chroma
# -------------------------------
async def add_chunks_to_chroma(chunks: List[Document], collection):
    """
    Adds document chunks into a ChromaDB collection.
    
    Steps:
    1. Fetch existing document IDs to avoid duplicates.
    2. Iterate through each chunk:
        a. Generate embedding for the chunk using get_embeddings().
        b. Skip chunk if embedding is empty.
        c. Delete old chunk in collection if ID already exists.
        d. Add chunk content, metadata, and embedding to collection.
    
    - 'chunks': List of Document objects.
    - 'collection': ChromaDB collection object.
    - Logs errors or warnings for failures.
    """
    existing_ids = set()

    # Fetch existing document IDs
    try:
        results = collection.get()  # Default returns existing IDs and documents
        existing_ids = set(results['ids']) if 'ids' in results else set()
    except Exception as e:
        log.warning(f"Failed to fetch existing IDs: {e}")
        traceback.print_exc()

    # Iterate and add each chunk
    for i, chunk in enumerate(chunks):
        chunk_id = f"chunk_{i}"  # Unique ID for chunk

        vector = await get_embeddings(chunk.page_content)
        if not vector:
            log.warning(f"Skipping {chunk_id} due to empty embedding")
            continue

        # Delete old chunk if it exists
        if chunk_id in existing_ids:
            try:
                collection.delete(ids=[chunk_id])
            except Exception as e:
                log.error(f"Failed to delete existing {chunk_id}: {e}", exc_info=True)

        # Add new chunk to collection
        try:
            collection.add(
                documents=[chunk.page_content],
                metadatas=[{"source": chunk_id}],
                embeddings=[vector],
                ids=[chunk_id]
            )
        except Exception as e:
            log.error(f"Failed to add {chunk_id} to collection: {e}", exc_info=True)
