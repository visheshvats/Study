from langchain_core.documents import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter, TokenTextSplitter

def demonstrate_recursive_splitter():
    print("--- 1. Recursive Character Text Splitter ---")
    # This is the industry standard splitter.
    # It tries to split on double newlines \n\n (paragraphs), 
    # then single newlines \n, then periods, then spaces, then chars.
    
    text = (
        "Phase 1: Planning. We will gather requirements and set milestones.\n\n"
        "Phase 2: Development. Engineers will write code. This is a very long sentence "
        "that might need to be split if the chunk size is small enough.\n\n"
        "Phase 3: Testing. QA will verify the features."
    )
    
    doc = Document(page_content=text, metadata={"source": "project_plan.txt"})
    
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=70,       # Max characters per chunk
        chunk_overlap=15,    # Characters to overlap between chunks
        length_function=len,
    )
    
    chunks = splitter.split_documents([doc])
    
    print(f"Original length: {len(text)} chars")
    print(f"Created {len(chunks)} chunks:")
    for i, c in enumerate(chunks):
        print(f"\n[Chunk {i+1}] ({len(c.page_content)} chars)")
        print(c.page_content)

def demonstrate_token_splitter():
    print("\n--- 2. Token Text Splitter ---")
    # Useful when you have strict LLM context window limits and need exact token counts.
    # Note: Requires 'tiktoken' package in a real environment.
    
    text = "The quick brown fox jumps over the lazy dog. " * 10
    
    # Mocking Token Splitter for this exercise without tiktoken dependency
    print("Mocking Token Splitter (splits by approx words):")
    chunk_size = 15 # Words
    chunk_overlap = 5
    
    words = text.split()
    chunks = []
    
    for i in range(0, len(words), chunk_size - chunk_overlap):
        chunk_words = words[i : i + chunk_size]
        chunks.append(" ".join(chunk_words))
        if i + chunk_size >= len(words):
            break
            
    for i, c in enumerate(chunks):
        print(f"Chunk {i+1}: {c}")

if __name__ == "__main__":
    demonstrate_recursive_splitter()
    demonstrate_token_splitter()
