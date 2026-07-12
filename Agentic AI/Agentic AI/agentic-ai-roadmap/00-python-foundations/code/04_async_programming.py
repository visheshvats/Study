import asyncio
import httpx
from typing import List
import time

# Java: CompletableFuture<String> = CompletableFuture.supplyAsync(() -> fetch(url))
# Python:
async def fetch_data(url: str, delay: int = 0) -> dict:
    """
    Mocks an HTTP request.
    We use httpx (async version of requests).
    """
    print(f"Started fetching {url}...")
    # Simulate network delay WITHOUT blocking the event loop
    await asyncio.sleep(delay) 
    
    # In a real scenario, you would do:
    # async with httpx.AsyncClient(timeout=30.0) as client:
    #     response = await client.get(url)
    #     response.raise_for_status()
    #     return response.json()
        
    print(f"Finished fetching {url}!")
    return {"url": url, "status": "success"}

# Parallel execution — Java: CompletableFuture.allOf(f1, f2, f3).join()
async def fetch_all(urls: List[str]) -> List[dict]:
    # Creates a list of Coroutine objects (they haven't started running yet)
    tasks = [fetch_data(url, delay=1) for url in urls]
    
    # Gather runs them concurrently. It waits for all to finish.
    results = await asyncio.gather(*tasks, return_exceptions=True)
    return [r for r in results if not isinstance(r, Exception)]

# Async generator (streaming)
async def stream_tokens(prompt: str):
    """Simulates streaming token-by-token (like LLM outputs)."""
    words = prompt.split()
    for word in words:
        await asyncio.sleep(0.2)   # simulate network delay per token
        yield word + " "

# Consume stream
async def print_stream():
    print("Streaming started:")
    async for token in stream_tokens("Hello streaming world from async Python!"):
        # flush=True is important to print immediately to console
        print(token, end="", flush=True) 
    print("\nStreaming finished.")

async def main():
    start = time.time()
    
    print("--- Parallel Execution ---")
    urls = ["api/user/1", "api/user/2", "api/user/3"]
    # If run sequentially, this would take 3 seconds.
    # Concurrently, it takes ~1 second.
    results = await fetch_all(urls)
    print(f"Results: {results}")
    
    print("\n--- Streaming ---")
    await print_stream()
    
    print(f"\nTotal execution time: {time.time() - start:.2f} seconds")

# Entry point
if __name__ == "__main__":
    # asyncio.run() creates the event loop, runs the main coroutine, and closes it.
    asyncio.run(main())
