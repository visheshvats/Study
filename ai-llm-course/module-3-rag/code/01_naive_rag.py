"""
MODULE 3 — Example 1: Naive RAG (Simplest Implementation)
===========================================================
The simplest possible RAG pipeline in ~50 lines of core logic.

This shows that RAG is fundamentally just:
  1. Search your documents
  2. Paste results into prompt
  3. Ask LLM

SETUP:
  pip install openai chromadb python-dotenv

RUN:
  python 01_naive_rag.py
"""

import os
from dotenv import load_dotenv
from openai import OpenAI
import chromadb

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


# ══════════════════════════════════════════════════════
# STEP 1: INDEX — Store documents in vector DB
# (In production, this runs once or on a schedule)
# ══════════════════════════════════════════════════════

def create_knowledge_base() -> chromadb.Collection:
    """
    Create a simple knowledge base from a list of documents.
    
    In production, these would come from:
    - Confluence/Notion pages
    - PDF files
    - Database records
    - API responses
    """
    chroma = chromadb.Client()
    collection = chroma.create_collection(name="company_knowledge")

    # Simulating company knowledge (in production, load from files/APIs)
    documents = [
        # HR Policy
        "Our refund policy allows full refunds within 30 days of purchase. "
        "After 30 days, we offer store credit only. Digital products are "
        "non-refundable once downloaded. To request a refund, email "
        "support@company.com with your order number.",

        # Engineering
        "Our tech stack uses Spring Boot 3.2 with Java 21 for backend services. "
        "We use PostgreSQL 16 as our primary database and Redis for caching. "
        "All services communicate via Apache Kafka for async processing. "
        "Frontend is built with React 18 and TypeScript.",

        # DevOps
        "Deployments happen every Tuesday and Thursday at 2 PM EST. "
        "All changes must pass CI/CD pipeline with >80% code coverage. "
        "We use GitHub Actions for CI and ArgoCD for Kubernetes deployments. "
        "Hotfixes can be deployed anytime with VP Engineering approval.",

        # Product
        "Our product supports three pricing tiers: Free (up to 100 users), "
        "Pro ($49/month, up to 1000 users, priority support), and Enterprise "
        "(custom pricing, unlimited users, dedicated support, SLA guarantee). "
        "All plans include a 14-day free trial.",

        # Engineering standards
        "All API endpoints must follow RESTful conventions. Use nouns for "
        "resources (GET /users, POST /orders). Include pagination for list "
        "endpoints (page, size parameters). Rate limiting is set at 100 "
        "requests per minute per API key. Authentication uses OAuth2 JWT tokens.",

        # On-call
        "On-call rotation follows a weekly schedule. Primary on-call responds "
        "within 15 minutes for P0 incidents. Secondary on-call is backup. "
        "Escalation path: On-call → Team Lead → Engineering Manager → VP. "
        "All incidents must have a postmortem within 48 hours.",

        # Architecture
        "Our microservices architecture has 12 services. The API Gateway "
        "(Spring Cloud Gateway) handles routing and rate limiting. Service "
        "discovery uses Kubernetes DNS. Circuit breakers are implemented with "
        "Resilience4j. All inter-service communication is async via Kafka "
        "except for user-facing read operations which use synchronous REST.",
    ]

    metadatas = [
        {"source": "hr-policy.md", "topic": "hr"},
        {"source": "tech-stack.md", "topic": "engineering"},
        {"source": "deployment-guide.md", "topic": "devops"},
        {"source": "pricing-page.md", "topic": "product"},
        {"source": "api-standards.md", "topic": "engineering"},
        {"source": "oncall-guide.md", "topic": "operations"},
        {"source": "architecture.md", "topic": "engineering"},
    ]

    collection.add(
        documents=documents,
        metadatas=metadatas,
        ids=[f"doc_{i}" for i in range(len(documents))],
    )

    print(f"  📚 Knowledge base created: {collection.count()} documents")
    return collection


# ══════════════════════════════════════════════════════
# STEP 2: RETRIEVE — Search for relevant documents
# ══════════════════════════════════════════════════════

def retrieve(collection: chromadb.Collection, query: str, n_results: int = 3) -> list[dict]:
    """
    Search the knowledge base for relevant documents.
    
    This is the "R" in RAG — Retrieval.
    ChromaDB handles embedding + search automatically.
    """
    results = collection.query(
        query_texts=[query],
        n_results=n_results,
    )

    retrieved = []
    for i in range(len(results["documents"][0])):
        retrieved.append({
            "text": results["documents"][0][i],
            "source": results["metadatas"][0][i]["source"],
            "distance": results["distances"][0][i],
        })

    return retrieved


# ══════════════════════════════════════════════════════
# STEP 3: GENERATE — Ask LLM with retrieved context
# ══════════════════════════════════════════════════════

def generate_answer(query: str, retrieved_docs: list[dict]) -> str:
    """
    Use LLM to generate an answer based on retrieved documents.
    
    This is the "AG" in RAG — Augmented Generation.
    The LLM sees the documents IN the prompt, not in its training data.
    """
    # Build the context section
    context = "\n---\n".join(
        f"Source: {doc['source']}\n{doc['text']}"
        for doc in retrieved_docs
    )

    # THE RAG PROMPT — this is the core pattern
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a helpful company assistant. Answer questions based ONLY "
                    "on the provided context documents. Follow these rules:\n"
                    "1. If the answer is found in the context, provide it clearly\n"
                    "2. If the answer is NOT in the context, say: 'I don't have "
                    "enough information to answer that based on available documents.'\n"
                    "3. Always cite the source document using [Source: filename]\n"
                    "4. Do NOT make up information that's not in the context"
                ),
            },
            {
                "role": "user",
                "content": (
                    f"Context documents:\n"
                    f"{context}\n\n"
                    f"---\n"
                    f"Question: {query}\n\n"
                    f"Answer (with source citations):"
                ),
            },
        ],
        temperature=0.1,  # Low temp for factual answers
    )

    return response.choices[0].message.content


# ══════════════════════════════════════════════════════
# THE COMPLETE RAG PIPELINE
# ══════════════════════════════════════════════════════

def rag_query(collection: chromadb.Collection, query: str) -> str:
    """
    The complete RAG pipeline in 3 lines:
    1. Retrieve relevant documents
    2. Generate answer with context
    3. Return answer

    That's it. This is what Perplexity, ChatGPT with browsing,
    and every enterprise Q&A bot does at its core.
    """
    retrieved = retrieve(collection, query, n_results=3)
    answer = generate_answer(query, retrieved)
    return answer, retrieved


# ══════════════════════════════════════════════════════
# DEMO
# ══════════════════════════════════════════════════════

def main():
    print("╔══════════════════════════════════════════════╗")
    print("║  📖 Naive RAG — Simplest Implementation      ║")
    print("║  Search + Paste + Ask = RAG                  ║")
    print("╚══════════════════════════════════════════════╝\n")

    # Create knowledge base
    collection = create_knowledge_base()

    # Test queries
    queries = [
        "What is our refund policy?",
        "What tech stack do we use?",
        "How often do deployments happen?",
        "What are our pricing plans?",
        "What is the meaning of life?",      # ← Should say "I don't know"
        "How does our on-call rotation work?",
    ]

    for query in queries:
        print(f"\n  {'═'*55}")
        print(f"  🔍 Question: {query}")
        print(f"  {'─'*55}")

        answer, retrieved = rag_query(collection, query)

        # Show what was retrieved
        print(f"\n  📄 Retrieved {len(retrieved)} documents:")
        for i, doc in enumerate(retrieved, 1):
            print(f"    {i}. [{doc['source']}] (dist: {doc['distance']:.3f})")

        # Show the answer
        print(f"\n  🤖 Answer:")
        for line in answer.split("\n"):
            print(f"    {line}")

    print(f"\n\n  {'═'*55}")
    print(f"  ✅ That's Naive RAG — simple but effective!")
    print(f"  Next: See 03_advanced_rag.py for production patterns.\n")


if __name__ == "__main__":
    main()
