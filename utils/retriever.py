import traceback
import warnings
from utils.chroma_utils import get_embeddings  # Function to generate vector embeddings
from utils.logger import log  # Custom logger instance

# Suppress unwanted warnings for cleaner logs
warnings.filterwarnings('ignore')


async def retrieve_documents(question, collection, top_k=2):
    """
    Retrieve relevant documents from ChromaDB based on the input question.

    Steps:
    1. Generate a vector embedding for the input question using the embedding model.
    2. Query the ChromaDB collection for the top_k most similar documents.
    3. Extract the actual document text from the query results.

    Args:
        question (str): The input query/question from the user.
        collection: ChromaDB collection object to search against.
        top_k (int, optional): Number of top documents to retrieve. Defaults to 2.

    Returns:
        list: List of retrieved document texts.
              Returns an empty list if no documents found or if an error occurs.
    """
    try:
        # ------------------------------
        # Step 1: Generate embedding
        # ------------------------------
        # Converts the question into a numerical vector for semantic similarity search
        question_embedding = await get_embeddings(question)

        # ------------------------------
        # Step 2: Query ChromaDB collection
        # ------------------------------
        # n_results specifies how many closest documents to return
        results = collection.query(
            query_embeddings=[question_embedding],
            n_results=top_k
        )

        # ------------------------------
        # Step 3: Extract document texts
        # ------------------------------
        documents = []
        if "documents" in results and results["documents"]:
            # results["documents"][0] contains the list of document texts
            for i in range(len(results["ids"][0])):
                documents.append(results["documents"][0][i])
        else:
            # Warn if no documents found
            log.warning("No documents found for the given query.")

        return documents

    except Exception as e:
        # ------------------------------
        # Error handling
        # ------------------------------
        # Logs the error message and prints traceback for debugging
        log.error(f"Error in retrieve_documents: {e}")
        traceback.print_exc()
        return []
