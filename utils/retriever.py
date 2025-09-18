import traceback
import warnings
from utils.chroma_utils import get_embeddings
from utils.logger import log  # Custom logger instance

# Suppress unwanted warnings for cleaner logs
warnings.filterwarnings('ignore')


async def retrieve_documents(question, collection, top_k=2):
    """
    Retrieve relevant documents from ChromaDB based on the input question.

    Args:
        question (str): The input query/question from the user.
        collection: ChromaDB collection object to search against.
        top_k (int): Number of top documents to retrieve (default=2).

    Returns:
        list: List of retrieved documents. Returns an empty list if no documents found or an error occurs.
    """
    try:
        # Step 1: Generate embedding for the user question
        question_embedding = await get_embeddings(question)

        # Step 2: Query ChromaDB collection with generated embedding
        results = collection.query(
            query_embeddings=[question_embedding],
            n_results=top_k
        )

        # Step 3: Extract documents from the query results
        documents = []
        if "documents" in results and results["documents"]:
            for i in range(len(results["ids"][0])):
                documents.append(results["documents"][0][i])
        else:
            log.warning("No documents found for the given query.")

        return documents

    except Exception as e:
        # Log the error and traceback for debugging
        log.error(f"Error in retrieve_documents: {e}")
        traceback.print_exc()
        return []
