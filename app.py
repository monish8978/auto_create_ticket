import os, traceback, requests, re, json
from fastapi import FastAPI, UploadFile, File, HTTPException, Request, Form
from fastapi.responses import JSONResponse
from prompt_template import custom_prompt, custom_prompt_solution_chat
from langchain_community.chat_message_histories import RedisChatMessageHistory
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, AIMessage
from fastapi.middleware.cors import CORSMiddleware
from utils.pdf_utils import extract_file_text
from utils.chroma_utils import (
    split_text, get_chroma_client, get_or_create_collection, add_chunks_to_chroma
)
from utils.retriever import retrieve_documents
from settings import PORT, REDIS_URL, BITNET_URL, BITNET_MODEL_NAME, GROQ_API_KEY, GROQ_MODEL
from utils.logger import log
import warnings

# Suppress unwanted warnings for cleaner logs (optional)
warnings.filterwarnings('ignore')

# ------------------------------
# Initialize FastAPI app
# ------------------------------
app = FastAPI(title="PDF Vector Store API", version="1.0")

# ------------------------------
# Enable CORS for API calls
# ------------------------------
# ⚠️ In production, restrict origins to trusted domains
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==========================
# API: Upload PDF or Raw Text
# ==========================
@app.post("/upload-pdf")
async def upload_pdf(
    file: UploadFile = File(None),
    file_str: str = Form(None),
    collection_name: str = Form(...)
):
    """
    Upload a file (PDF, DOCX, TXT, etc.) or raw string,
    extract text content, split it into chunks, and store in ChromaDB.

    Args:
        file: Uploaded file.
        file_str: Optional raw text input.
        collection_name: Name of ChromaDB collection to store data.

    Returns:
        JSON with status, number of chunks processed, and total tokens.
    """
    try:
        # ------------------------------
        # Step 1: Extract text
        # ------------------------------
        if file:
            # Save uploaded file temporarily
            file_path = f"temp_{file.filename}"
            with open(file_path, "wb") as f:
                f.write(await file.read())
            # Extract text using utility function
            text = extract_file_text(file_path)
            os.remove(file_path)  # Clean up temp file
        elif file_str:
            text = file_str
        else:
            log.error("No file or file_str provided in request.")
            raise HTTPException(status_code=400, detail="No file or file_str provided")

        if not text.strip():
            log.error("No text extracted from file or string.")
            raise ValueError("No text content extracted or provided")

        # ------------------------------
        # Step 2: Split text into chunks
        # ------------------------------
        # Helps with embedding and retrieval in ChromaDB
        chunks = split_text(text)

        # ------------------------------
        # Step 3: Store chunks in ChromaDB
        # ------------------------------
        client = get_chroma_client()
        collection = get_or_create_collection(client, collection_name)
        await add_chunks_to_chroma(chunks, collection)

        return JSONResponse({
            "detail": f"Text processed successfully for collection '{collection_name}'",
            "chunks_processed": len(chunks),
            "total_tokens": sum(len(chunk.page_content) for chunk in chunks)
        }, status_code=200)

    except Exception as e:
        log.error(f"Error in /upload-pdf: {e}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Failed to process input: {str(e)}")


# ==========================
# Helper: Extract Relevant Data
# ==========================
def extract_relevant_data(input_text):
    """
    Extract relevant section from input text based on patterns.

    1. Look for text between "---" markers.
    2. Fallback: Look for text starting with "Main Issue:".
    """
    pattern1 = r'---\s*(.*?)\s*---'
    matches = re.findall(pattern1, input_text, re.DOTALL)

    if not matches:
        pattern2 = r'Main Issue:.*?---'
        matches = re.findall(pattern2, input_text, re.DOTALL)

    return matches[0].strip() if matches else None


# ==========================
# API: Query Documents & Generate AI Response
# ==========================
@app.post("/query")
async def query_documents(request: Request):
    """
    Accepts user query, retrieves context from ChromaDB, and generates AI response
    via Hugging Face / Ollama API.
    """
    try:
        body = await request.json()
        subject = body.get("subject")
        mailBody = body.get("mailBody")
        session_id = body.get("session_id")
        collection_name = body.get("collection_name")

        if not session_id:
            raise HTTPException(status_code=400, detail="Session ID is required")

        # ------------------------------
        # Step 1: Combine subject and mail body
        # ------------------------------
        query_ask = subject + "\n" + mailBody

        # ------------------------------
        # Step 2: Retrieve conversation history from Redis
        # ------------------------------
        chat_history = RedisChatMessageHistory(session_id=session_id, url=REDIS_URL)
        past_dialogue = [msg.content for msg in chat_history.messages if isinstance(msg, HumanMessage)][-3:]
        full_query = " ".join(past_dialogue + [query_ask])

        # ------------------------------
        # Step 3: Retrieve top-k documents from ChromaDB
        # ------------------------------
        client = get_chroma_client()
        collection = get_or_create_collection(client, collection_name)
        results = await retrieve_documents(full_query, collection, top_k=3)
        context_tmp = "\n\n".join(results)
        context = extract_relevant_data(context_tmp) or context_tmp

        # ------------------------------
        # Step 4: Prepare system prompt
        # ------------------------------
        system_prompt = custom_prompt.format(context=context, question=query_ask)

        # ------------------------------
        # Step 5: Prepare payload for AI API
        # ------------------------------
        payload = {
            "model": BITNET_MODEL_NAME,
            "messages": [{"role": "user", "content": system_prompt}],
            "stream": False,
            "think": False
        }
        headers = {"Content-Type": "application/json"}

        response_api = requests.post(BITNET_URL, headers=headers, data=json.dumps(payload))
        response_api.raise_for_status()
        response_data = response_api.json()

        # ------------------------------
        # Step 6: Clean and format response
        # ------------------------------
        response_text_tmp = response_data.get("message", {}).get("content", "").strip()
        response_text_cleaned = re.sub(r'[\x00-\x1F\x7F]', '', response_text_tmp)
        response_text = json.loads(response_text_cleaned)
        response_text['solution'] = response_text['solution'].replace('\n', '\\n')

        # Save conversation back to Redis
        chat_history.add_user_message(query_ask)
        chat_history.add_ai_message(response_text_tmp)

        # ------------------------------
        # Step 7: Build Adaptive Card style response
        # ------------------------------
        response = {
            "type": "adaptiveCard",
            "body": [
                {"type": "TextBlock", "text": response_text},
                {"type": "TextBlock", "text": "Was I helpful?"},
                {
                    "type": "Button",
                    "id": "serviceType",
                    "style": "expanded",
                    "choices": [
                        {"id": "Yes", "title": "Yes", "value": "Yes"},
                        {"id": "No", "title": "No", "value": "No"}
                    ]
                }
            ],
            "actions": []
        }

        return JSONResponse(response, status_code=200)

    except Exception as e:
        log.error(f"Error in /query: {e}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Failed to retrieve documents: {str(e)}")


# ==========================
# API: Solution Chat (Groq LLM)
# ==========================
@app.post("/solution-chat")
async def solution_chat(request: Request):
    """
    Query ChromaDB and return AI response using Groq LLM.
    """
    try:
        body = await request.json()
        query_ask = body.get("user_query")
        session_id = body.get("session_id")
        collection_name = "auto_ticket_creation"

        if not session_id:
            raise HTTPException(status_code=400, detail="Session ID is required")

        # Retrieve last 3 user messages from Redis
        chat_history = RedisChatMessageHistory(session_id=session_id, url=REDIS_URL)
        past_dialogue = [
            msg.content for msg in chat_history.messages if isinstance(msg, HumanMessage)
        ][-3:]
        full_query = " ".join(past_dialogue + [query_ask])

        # Retrieve top 3 documents from Chroma
        client = get_chroma_client()
        collection = get_or_create_collection(client, collection_name)
        results = await retrieve_documents(full_query, collection, top_k=3)
        context_tmp = "\n\n".join(results)
        context = extract_relevant_data(context_tmp) or context_tmp

        # Prepare prompt for Groq
        system_prompt = custom_prompt_solution_chat.format(context=context, question=query_ask)

        # Initialize Groq LLM
        groq_llm = ChatGroq(
            model=GROQ_MODEL,
            temperature=0,
            max_tokens=500,
            api_key=os.getenv("GROQ_API_KEY", GROQ_API_KEY)
        )

        # Query Groq
        response = groq_llm.invoke([
            {"role": "system", "content": "You are Zeni, a helpful assistant."},
            {"role": "user", "content": system_prompt}
        ])
        response_payload = response.content.strip()

        # Save conversation to Redis
        chat_history.add_user_message(query_ask)
        chat_history.add_ai_message(response_payload)

        return JSONResponse(response_payload, status_code=200)

    except Exception as e:
        log.error(f"Error in /solution-chat: {e}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Failed to retrieve documents: {str(e)}")


# ==========================
# Run the App
# ==========================
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=PORT)
