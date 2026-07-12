import asyncio
from fastapi import FastAPI
from fastapi.responses import StreamingResponse
import uvicorn
from pydantic import BaseModel

app = FastAPI(title="Streaming API")

class StreamRequest(BaseModel):
    message: str

async def mock_llm_stream(prompt: str):
    """Simulates an LLM returning tokens one by one."""
    words = [
        "This ", "is ", "a ", "simulated ", "streaming ", 
        "response ", "from ", "the ", "LLM ", "API."
    ]
    
    for word in words:
        await asyncio.sleep(0.3) # Simulate processing delay
        # Format required for Server-Sent Events (SSE)
        yield f"data: {word}\n\n"
        
    yield "data: [DONE]\n\n"

@app.post("/chat/stream")
async def chat_stream(request: StreamRequest):
    """
    Endpoint that streams Server-Sent Events.
    Like Java's ResponseBodyEmitter.
    """
    return StreamingResponse(
        mock_llm_stream(request.message), 
        media_type="text/event-stream"
    )

if __name__ == "__main__":
    print("Starting Streaming API Server...")
    print("To test, run in another terminal:")
    print('curl -X POST http://localhost:8001/chat/stream -H "Content-Type: application/json" -d "{\\"message\\": \\"Hello\\"}"')
    
    # Running on 8001 to avoid conflict if 8000 is used elsewhere
    uvicorn.run(app, host="127.0.0.1", port=8001)
