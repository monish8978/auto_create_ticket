import os, traceback, requests
from fastapi import FastAPI, UploadFile, File, HTTPException, Request, Form
from fastapi.responses import JSONResponse
from prompt_template import custom_prompt
from langchain.memory.chat_message_histories import RedisChatMessageHistory
from langchain.schema import HumanMessage, AIMessage
from fastapi.middleware.cors import CORSMiddleware
from utils.pdf_utils import extract_file_text
from utils.chroma_utils import (
    split_text, get_chroma_client, get_or_create_collection, add_chunks_to_chroma
)
from utils.retriever import retrieve_documents
from settings import PORT,REDIS_URL, BITNET_URL, BITNET_MODEL_NAME
from utils.logger import log
import warnings

# Suppress unwanted warnings (not always recommended in production)
warnings.filterwarnings('ignore')

# Initialize FastAPI app
app = FastAPI(title="PDF Vector Store API", version="1.0")

# Enable CORS (Cross-Origin Resource Sharing) for API calls
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # ⚠️ In production, restrict to trusted domains
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==========================
# API: Upload PDF / String
# ==========================
@app.post("/upload-pdf")
async def upload_pdf(
    file: UploadFile = File(None), 
    file_str: str = Form(None), 
    collection_name: str = Form(...)
):
    """
    Upload a file or raw text, extract content, split into chunks,
    and store in ChromaDB for later retrieval.
    """
    try:
        # 1️⃣ Decide source: File upload or raw string
        if file:
            file_path = f"temp_{file.filename}"
            with open(file_path, "wb") as f:
                f.write(await file.read())

            # Extract text
            text = extract_file_text(file_path)
            os.remove(file_path)

        elif file_str:
            text = file_str
        else:
            log.error("No file or file_str provided in request.")
            raise HTTPException(status_code=400, detail="No file or file_str provided")

        if not text.strip():
            log.error("No text extracted from file or string.")
            raise ValueError("No text content extracted or provided")

        # 2️⃣ Split text into chunks
        chunks = split_text(text)

        # 3️⃣ Store chunks in ChromaDB
        client = get_chroma_client()
        collection = get_or_create_collection(client, collection_name)
        await add_chunks_to_chroma(chunks, collection)

        return JSONResponse({
            "detail": f" Text processed successfully for collection '{collection_name}'",
            "chunks_processed": len(chunks),
            "total_tokens": sum(len(chunk.page_content) for chunk in chunks)
        }, status_code=200)

    except Exception as e:
        log.error(f"Error in /upload-pdf: {e}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Failed to process input: {str(e)}")


# ==========================
# API: Query Documents
# ==========================
@app.post("/query")
async def query_documents(request: Request):
    """
    Query ChromaDB with user input and return AI-generated response
    using Hugging Face inference API.
    """
    try:
        body = await request.json()
        subject = body.get("subject")
        mailBody = body.get("mailBody")
        session_id = body.get("session_id")
        collection_name = body.get("collection_name")

        # 1️⃣ Combine subject + mail body
        query_ask = subject + "\n" + mailBody

        # 2️⃣ Retrieve past conversation from Redis
        chat_history = RedisChatMessageHistory(session_id=session_id, url=REDIS_URL)
        past_dialogue = [msg.content for msg in chat_history.messages if isinstance(msg, HumanMessage)][-3:]
        full_query = " ".join(past_dialogue + [query_ask])

        # 3️⃣ ChromaDB retrieval
        client = get_chroma_client()
        collection = get_or_create_collection(client, collection_name)
        results = await retrieve_documents(full_query, collection, top_k=3)
        context = "\n\n".join(results)

        # 4️⃣ Prepare system prompt
        system_prompt = custom_prompt.format(context=context, question=query_ask)

        # Keep short history for better performance
        history_messages = chat_history.messages[-5:]
        history_messages.append(HumanMessage(content=query_ask))
        history_messages.insert(0, AIMessage(content=system_prompt))

        # 5️⃣ Format messages for HF Inference API
        formatted_messages = []
        for msg in history_messages:
            role = "user" if isinstance(msg, HumanMessage) else "assistant"
            formatted_messages.append({"role": role, "content": msg.content})

        # 6️⃣ Call BitNet completions API instead of HF inference API
        payload = {
            "model": BITNET_MODEL_NAME,
            "prompt": system_prompt + f"\nUser: {query_ask}\nAssistant:",
            "max_tokens": 200,
            "temperature": 0.3,
            "stop": ["User:", "Assistant:"]
        }

        # Send request
        response_api = requests.post(
            BITNET_URL,
            headers={"Content-Type": "application/json"},
            json=payload
        )
        response_api.raise_for_status()
        response_data = response_api.json()

        # Extract response text
        response_text = response_data.get("content", "").strip()


        # 7️⃣ Save conversation back to Redis
        chat_history.add_user_message(query_ask)
        chat_history.add_ai_message(response_text)

        # 8️⃣ Build Adaptive Card style response
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
# Run the App
# ==========================
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=PORT)
