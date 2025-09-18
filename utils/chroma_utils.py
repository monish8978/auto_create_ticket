import chromadb
from settings import OLLAMA_URL, OLLAMA_MODEL_NAME 
from chromadb.config import Settings
from langchain.text_splitter import RecursiveCharacterTextSplitter
import httpx
from typing import List
import traceback
from langchain.schema.document import Document
from utils.logger import log
import warnings

# Suppress unnecessary warnings
warnings.filterwarnings('ignore')


def split_text(text: str) -> List[Document]:
    """
    Splits input text into chunks for better embedding performance.
    Uses RecursiveCharacterTextSplitter to ensure overlap for context.
    """
    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    chunks = splitter.create_documents([text])
    return chunks


async def get_embeddings(text: str):
    """
    Fetches embeddings for the given text from Hugging Face inference API.
    Returns a vector embedding list.
    """
    payload = {
        "model": OLLAMA_MODEL_NAME ,
        "prompt": text   # Input text for embedding
    }

    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(OLLAMA_URL, json=payload)
            response.raise_for_status()
            data = response.json()
            vector = data.get("embedding", [])

            if vector == []:
                log.warning("Empty embedding vector received")

            return vector
    except Exception as e:
        log.error(f"Failed to fetch embedding: {e}", exc_info=True)
        return []


def get_chroma_client(path="./chroma_data_db"):
    """
    Initializes and returns a ChromaDB PersistentClient.
    Data will be stored at the given path.
    """
    return chromadb.PersistentClient(path=path, settings=Settings(anonymized_telemetry=False))


def get_or_create_collection(client, name):
    """
    Retrieves an existing collection from ChromaDB.
    If it doesn't exist, creates a new collection.
    """
    try:
        return client.get_collection(name=name)
    except Exception as e:
        log.warning(f"Collection '{name}' not found. Creating new one. Error={e}")
        return client.create_collection(name=name)


async def add_chunks_to_chroma(chunks: List[Document], collection):
    """
    Adds document chunks into the given ChromaDB collection.
    - Creates embeddings for each chunk
    - Deletes old chunk ID if it already exists
    - Stores new documents with metadata
    """
    existing_ids = set()

    # Fetch existing document IDs (to avoid duplicates)
    try:
        results = collection.get()   # By default returns existing ids
        existing_ids = set(results['ids']) if 'ids' in results else set()
    except Exception as e:
        log.warning(f"Failed to fetch existing IDs: {e}")
        traceback.print_exc()

    for i, chunk in enumerate(chunks):
        chunk_id = f"chunk_{i}"

        vector = await get_embeddings(chunk.page_content)
        if not vector:
            log.warning(f"Skipping {chunk_id} due to empty embedding")
            continue

        # If chunk already exists, delete it before adding new one
        if chunk_id in existing_ids:
            try:
                collection.delete(ids=[chunk_id])
            except Exception as e:
                log.error(f"Failed to delete existing {chunk_id}: {e}", exc_info=True)

        try:
            collection.add(
                documents=[chunk.page_content],
                metadatas=[{"source": chunk_id}],
                embeddings=[vector],
                ids=[chunk_id]
            )
        except Exception as e:
            log.error(f"Failed to add {chunk_id} to collection: {e}", exc_info=True)
