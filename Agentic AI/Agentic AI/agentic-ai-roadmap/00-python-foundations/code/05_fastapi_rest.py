from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel
from typing import Optional
import uvicorn
import uuid
import logging

# Configure basic logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app (Think of this as your Spring Boot application class)
app = FastAPI(title="Agentic AI Gateway", version="1.0.0")

# --- Models (like Spring @RequestBody / @ResponseBody DTOs) ---
class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = None
    temperature: float = 0.7

class ChatResponse(BaseModel):
    response: str
    session_id: str
    tokens_used: int

# --- In-memory store (replace with Redis in Phase 11) ---
sessions: dict = {}

# --- Middleware: request logging (Like Java Filters/Interceptors) ---
@app.middleware("http")
async def log_requests(request: Request, call_next):
    logger.info(f"→ {request.method} {request.url.path}")
    response = await call_next(request)
    logger.info(f"← {response.status_code}")
    return response

# --- Endpoints (@RestController mapped methods) ---
@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    if not request.message.strip():
        # Throws a 400 Bad Request
        raise HTTPException(status_code=400, detail="Message cannot be empty")

    session_id = request.session_id or str(uuid.uuid4())

    # Simulated LLM processing
    # TODO (Phase 1): Replace with actual Anthropic/OpenAI call
    response_text = f"Echo (mock LLM): You said '{request.message}'. (Temp: {request.temperature})"
    
    # Update in-memory session (Mock)
    if session_id not in sessions:
        sessions[session_id] = []
    sessions[session_id].append({"user": request.message, "ai": response_text})

    return ChatResponse(
        response=response_text,
        session_id=session_id,
        tokens_used=len(request.message.split()) * 2 # Mock token calculation
    )

@app.get("/health")
async def health():
    """Liveness probe for k8s/docker."""
    return {"status": "ok", "version": "1.0.0"}

if __name__ == "__main__":
    # uvicorn is the ASGI web server (like Tomcat for Spring Boot)
    print("Starting Uvicorn server...")
    print("Visit http://127.0.0.1:8000/docs for Swagger UI")
    uvicorn.run(app, host="127.0.0.1", port=8000)
