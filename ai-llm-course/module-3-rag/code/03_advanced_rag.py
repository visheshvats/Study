"""
MODULE 3 — Example 3: Advanced RAG Patterns
=============================================
Production-grade RAG with multi-query, reranking, and citations.

SETUP:
  pip install openai chromadb python-dotenv

RUN:
  python 03_advanced_rag.py
"""

import os
import json
from dotenv import load_dotenv
from openai import OpenAI
import chromadb

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def create_knowledge_base() -> chromadb.Collection:
    """Create a richer knowledge base for advanced demos."""
    chroma = chromadb.Client()
    collection = chroma.create_collection(name="advanced_kb")

    docs = [
        {"text": "Spring Boot auto-configuration works by scanning the classpath for specific classes. When it finds spring-boot-starter-web, it automatically configures an embedded Tomcat server, sets up Spring MVC, and registers default error handlers. You can override any auto-configuration by defining your own beans.", "source": "spring-boot-docs.md", "topic": "spring"},
        {"text": "Spring Boot Actuator provides production-ready features: /health endpoint for liveness probes, /metrics for Prometheus integration, /info for build information, and /env for environment properties. Secure actuator endpoints in production by restricting access via Spring Security.", "source": "spring-actuator.md", "topic": "spring"},
        {"text": "HikariCP is the default connection pool in Spring Boot. Key settings: maximum-pool-size (default 10), minimum-idle, connection-timeout (30s default), and idle-timeout. For high-throughput services, increase maximum-pool-size to match your concurrent database connections needs.", "source": "hikari-tuning.md", "topic": "database"},
        {"text": "PostgreSQL EXPLAIN ANALYZE shows the actual execution plan of a query. Look for sequential scans on large tables (add an index), nested loops with high row counts (consider hash joins), and high actual time values. Use pg_stat_statements extension to find the most expensive queries.", "source": "postgres-performance.md", "topic": "database"},
        {"text": "Circuit breaker pattern in Resilience4j has three states: CLOSED (normal), OPEN (failing, fast-fail), and HALF_OPEN (testing recovery). Configure failureRateThreshold (percentage), waitDurationInOpenState, and permittedNumberOfCallsInHalfOpenState. Combine with retry and timeout for resilient services.", "source": "resilience4j-guide.md", "topic": "architecture"},
        {"text": "Kafka consumer lag is the difference between the latest offset and the consumer's current offset. Monitor using kafka-consumer-groups.sh or JMX metrics. High lag indicates consumers can't keep up. Solutions: increase partitions, add consumers to the group, optimize message processing, or use batch processing.", "source": "kafka-monitoring.md", "topic": "kafka"},
        {"text": "OAuth2 JWT tokens in Spring Security: Use spring-boot-starter-oauth2-resource-server. Configure the issuer-uri in application.yml pointing to your auth server (Keycloak, Auth0). The JWT is validated on every request without calling the auth server (stateless). Use @PreAuthorize for method-level security.", "source": "spring-security.md", "topic": "security"},
        {"text": "Docker multi-stage builds reduce image size by 90%. Stage 1: Use maven:3.9-amazoncorretto-21 to build the JAR. Stage 2: Use amazoncorretto:21-alpine as the runtime image, copy only the JAR from stage 1. This gives you a ~150MB image instead of ~800MB.", "source": "docker-optimization.md", "topic": "devops"},
    ]

    collection.add(
        documents=[d["text"] for d in docs],
        metadatas=[{"source": d["source"], "topic": d["topic"]} for d in docs],
        ids=[f"doc_{i}" for i in range(len(docs))],
    )

    return collection


# ══════════════════════════════════════════════════════
# ADVANCED PATTERN 1: Multi-Query Retrieval
# ══════════════════════════════════════════════════════

def multi_query_retrieve(collection, user_query: str, n_results: int = 3) -> list[dict]:
    """
    Generate multiple search queries from one user question.
    
    Why? A single query might miss relevant docs.
    "How to make my app faster?" could mean:
      - Database optimization
      - Caching strategies
      - Connection pool tuning
      - Code-level performance
    
    By generating multiple queries, we cast a wider net.
    """
    print(f"\n  🔀 Multi-Query: Generating variant queries...")

    # Use LLM to generate alternative queries
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": (
                "Generate 3 different search queries for the given question. "
                "Each query should focus on a different aspect or use different "
                "terminology. Return JSON: {\"queries\": [\"q1\", \"q2\", \"q3\"]}"
            )},
            {"role": "user", "content": user_query}
        ],
        temperature=0.7,
        response_format={"type": "json_object"},
    )

    variants = json.loads(response.choices[0].message.content)
    queries = [user_query] + variants.get("queries", [])

    print(f"     Original: {user_query}")
    for i, q in enumerate(variants.get("queries", []), 1):
        print(f"     Variant {i}: {q}")

    # Search with each query and merge results
    seen_ids = set()
    all_results = []

    for query in queries:
        results = collection.query(query_texts=[query], n_results=n_results)
        for i in range(len(results["documents"][0])):
            doc_id = results["ids"][0][i]
            if doc_id not in seen_ids:
                seen_ids.add(doc_id)
                all_results.append({
                    "text": results["documents"][0][i],
                    "source": results["metadatas"][0][i]["source"],
                    "distance": results["distances"][0][i],
                    "found_by": query,
                })

    print(f"     Found {len(all_results)} unique documents (from {len(queries)} queries)")
    return all_results


# ══════════════════════════════════════════════════════
# ADVANCED PATTERN 2: LLM-based Reranking
# ══════════════════════════════════════════════════════

def rerank_with_llm(query: str, documents: list[dict], top_k: int = 3) -> list[dict]:
    """
    Use LLM to rerank documents by relevance.
    
    Vector search gives approximate results.
    LLM reranking gives precise relevance scores.
    
    In production, use Cohere Rerank API for speed.
    This LLM-based approach is for learning.
    """
    print(f"\n  🔄 Reranking {len(documents)} documents with LLM...")

    doc_list = "\n".join(
        f"Document {i}: {doc['text'][:200]}..."
        for i, doc in enumerate(documents)
    )

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": (
                "You are a relevance judge. Given a query and documents, "
                "score each document's relevance to the query from 0 to 10. "
                "Return JSON: {\"scores\": [{\"doc_index\": 0, \"score\": 8, \"reason\": \"...\"}]}"
            )},
            {"role": "user", "content": (
                f"Query: {query}\n\n"
                f"Documents:\n{doc_list}\n\n"
                f"Score each document's relevance (0-10):"
            )}
        ],
        temperature=0,
        response_format={"type": "json_object"},
    )

    scores = json.loads(response.choices[0].message.content)

    # Apply scores and sort
    for score_item in scores.get("scores", []):
        idx = score_item.get("doc_index", 0)
        if idx < len(documents):
            documents[idx]["relevance_score"] = score_item.get("score", 0)
            documents[idx]["relevance_reason"] = score_item.get("reason", "")

    # Sort by relevance score (highest first)
    documents.sort(key=lambda x: x.get("relevance_score", 0), reverse=True)

    for doc in documents[:top_k]:
        print(f"     [{doc.get('relevance_score', '?')}/10] {doc['source']}: {doc.get('relevance_reason', '')[:60]}")

    return documents[:top_k]


# ══════════════════════════════════════════════════════
# ADVANCED PATTERN 3: RAG with Source Citations
# ══════════════════════════════════════════════════════

def generate_cited_answer(query: str, documents: list[dict]) -> str:
    """
    Generate an answer with proper source citations.
    
    Every claim must cite its source document.
    This is essential for enterprise trust.
    """
    # Number each document for easy citation
    context = "\n\n".join(
        f"[{i+1}] Source: {doc['source']}\n{doc['text']}"
        for i, doc in enumerate(documents)
    )

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": (
                "You are a technical assistant. Answer based ONLY on the provided "
                "numbered documents. Rules:\n"
                "1. After EACH factual claim, add a citation like [1] or [2]\n"
                "2. If blending info from multiple docs, cite all: [1][3]\n"
                "3. If the answer isn't in the docs, say so clearly\n"
                "4. Be concise and technical\n"
                "5. At the end, list all cited sources"
            )},
            {"role": "user", "content": (
                f"Documents:\n{context}\n\n"
                f"Question: {query}"
            )}
        ],
        temperature=0.1,
    )

    return response.choices[0].message.content


# ══════════════════════════════════════════════════════
# ADVANCED PATTERN 4: Query Reformulation (Conversational)
# ══════════════════════════════════════════════════════

def reformulate_query(chat_history: list[dict], current_query: str) -> str:
    """
    Rewrite a vague follow-up question into a standalone query.
    
    "What about its timeout?" → "What is the HikariCP connection timeout in Spring Boot?"
    """
    if not chat_history:
        return current_query

    history_text = "\n".join(
        f"{msg['role'].upper()}: {msg['content'][:100]}"
        for msg in chat_history[-4:]  # Last 4 messages for context
    )

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": (
                "Rewrite the user's follow-up question into a standalone search query. "
                "The query should be clear and include all necessary context from the "
                "conversation history. Return ONLY the rewritten query, nothing else."
            )},
            {"role": "user", "content": (
                f"Conversation history:\n{history_text}\n\n"
                f"Follow-up question: {current_query}\n\n"
                f"Standalone search query:"
            )}
        ],
        temperature=0,
        max_tokens=100,
    )

    reformulated = response.choices[0].message.content.strip()
    return reformulated


# ══════════════════════════════════════════════════════
# DEMO
# ══════════════════════════════════════════════════════

def main():
    print("╔══════════════════════════════════════════════╗")
    print("║  🚀 Advanced RAG Patterns                    ║")
    print("╚══════════════════════════════════════════════╝\n")

    collection = create_knowledge_base()
    print(f"  📚 Knowledge base: {collection.count()} documents\n")

    # ── Demo 1: Multi-Query Retrieval ──
    print("=" * 55)
    print("PATTERN 1: Multi-Query Retrieval")
    print("=" * 55)

    query1 = "How to improve my Spring Boot app performance?"
    docs = multi_query_retrieve(collection, query1)

    # ── Demo 2: Reranking ──
    print("\n" + "=" * 55)
    print("PATTERN 2: LLM-based Reranking")
    print("=" * 55)

    top_docs = rerank_with_llm(query1, docs, top_k=3)

    # ── Demo 3: Citations ──
    print("\n" + "=" * 55)
    print("PATTERN 3: Answer with Citations")
    print("=" * 55)

    answer = generate_cited_answer(query1, top_docs)
    print(f"\n  🤖 Answer:")
    for line in answer.split("\n"):
        print(f"    {line}")

    # ── Demo 4: Query Reformulation ──
    print("\n" + "=" * 55)
    print("PATTERN 4: Query Reformulation")
    print("=" * 55)

    chat_history = [
        {"role": "user", "content": "Tell me about HikariCP connection pool in Spring Boot"},
        {"role": "assistant", "content": "HikariCP is the default connection pool in Spring Boot with settings like maximum-pool-size (default 10), connection-timeout (30s)..."},
    ]
    followup = "What about its timeout settings?"

    reformulated = reformulate_query(chat_history, followup)
    print(f"\n  Original:     \"{followup}\"")
    print(f"  Reformulated: \"{reformulated}\"")
    print(f"  → Now we can search with a clear, standalone query!")

    print(f"\n\n{'='*55}")
    print("✅ Advanced RAG Summary:")
    print("  1. Multi-Query: Cast wider net with variant queries")
    print("  2. Reranking: LLM rescores documents for precision")
    print("  3. Citations: Every claim cites its source")
    print("  4. Reformulation: Convert vague follow-ups to clear queries\n")


if __name__ == "__main__":
    main()
