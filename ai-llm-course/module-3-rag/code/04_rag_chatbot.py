"""
MODULE 3 — PROJECT: Conversational RAG Chatbot
=================================================
A production-grade RAG chatbot that:
  1. Loads and chunks documents
  2. Indexes them in ChromaDB
  3. Maintains conversation history
  4. Reformulates follow-up questions
  5. Retrieves relevant context
  6. Generates cited answers
  7. Interactive REPL with commands

This is the Module 3 capstone — everything from Modules 0-3 combined!

SETUP:
  pip install openai chromadb python-dotenv

RUN:
  python 04_rag_chatbot.py

ARCHITECTURE:
  User Query
       │
       ▼
  ┌──────────────┐
  │  REFORMULATE │ ← Uses chat history to clarify ambiguous queries
  │  (if needed) │
  └──────┬───────┘
         │
         ▼
  ┌──────────────┐
  │   RETRIEVE   │ ← ChromaDB semantic search
  │   Top-K docs │
  └──────┬───────┘
         │
         ▼
  ┌──────────────┐
  │   GENERATE   │ ← LLM with context + history
  │   with cite  │
  └──────┬───────┘
         │
         ▼
  Answer + Sources
"""

import os
import re
import hashlib
from datetime import datetime
from dotenv import load_dotenv
from openai import OpenAI
import chromadb

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

MODEL = "gpt-4o-mini"


# ══════════════════════════════════════════════════════
# DOCUMENT PROCESSOR
# ══════════════════════════════════════════════════════

class DocumentProcessor:
    """Handles loading and chunking documents."""

    @staticmethod
    def chunk_text(text: str, chunk_size: int = 500, overlap: int = 50) -> list[str]:
        """Sentence-based chunking with overlap."""
        sentences = re.split(r'(?<=[.!?])\s+', text.strip())
        sentences = [s.strip() for s in sentences if s.strip() and len(s.strip()) > 10]

        chunks = []
        current_chunk = ""

        for sentence in sentences:
            if len(current_chunk) + len(sentence) > chunk_size and current_chunk:
                chunks.append(current_chunk.strip())
                # Keep overlap
                words = current_chunk.split()
                overlap_words = words[-overlap // 5:] if len(words) > overlap // 5 else words
                current_chunk = " ".join(overlap_words) + " " + sentence
            else:
                current_chunk += " " + sentence if current_chunk else sentence

        if current_chunk.strip():
            chunks.append(current_chunk.strip())

        return chunks


# ══════════════════════════════════════════════════════
# RAG CHATBOT
# ══════════════════════════════════════════════════════

class RAGChatbot:
    """
    A conversational RAG chatbot.
    
    Java Analogy:
      This is like a Spring Boot @Service with:
      - ChromaDB as the @Repository
      - OpenAI as the AI inference @Service
      - Chat history as the session state
    """

    def __init__(self):
        self.chroma = chromadb.Client()
        self.collection = self.chroma.get_or_create_collection(
            name="rag_chatbot",
            metadata={"hnsw:space": "cosine"},
        )
        self.processor = DocumentProcessor()
        self.chat_history: list[dict] = []
        self.sources_used: list[str] = []

    # ── Document Management ──

    def add_document(self, text: str, source: str = "manual", topic: str = "general"):
        """Add a document to the knowledge base."""
        chunks = self.processor.chunk_text(text)

        documents = []
        metadatas = []
        ids = []

        for i, chunk in enumerate(chunks):
            doc_id = hashlib.md5(f"{source}_{i}_{chunk[:30]}".encode()).hexdigest()
            documents.append(chunk)
            metadatas.append({
                "source": source,
                "topic": topic,
                "chunk_index": i,
                "total_chunks": len(chunks),
                "added_at": datetime.now().isoformat(),
            })
            ids.append(doc_id)

        self.collection.add(documents=documents, metadatas=metadatas, ids=ids)
        return len(chunks)

    def add_sample_data(self):
        """Load sample knowledge base for demo."""
        sample_docs = [
            {
                "text": "Spring Boot is a framework that simplifies Java application development. It provides auto-configuration, which automatically configures your application based on the dependencies you've added. For example, if you add spring-boot-starter-web, Spring Boot will auto-configure an embedded Tomcat server, Spring MVC, and default error handling. You can create a Spring Boot application using Spring Initializr (start.spring.io) or the spring init CLI command. The main class uses @SpringBootApplication annotation which combines @Configuration, @EnableAutoConfiguration, and @ComponentScan.",
                "source": "spring-boot-basics.md",
                "topic": "spring",
            },
            {
                "text": "Spring Boot Actuator provides production-ready features for monitoring and managing your application. Key endpoints include: /health for application health status (used by Kubernetes liveness/readiness probes), /metrics for application metrics (integrates with Prometheus and Grafana), /info for build and version information, /env for environment properties, and /loggers for runtime log level changes. In production, secure these endpoints using Spring Security - only expose /health and /info publicly, restrict others to admin roles.",
                "source": "spring-actuator.md",
                "topic": "spring",
            },
            {
                "text": "Apache Kafka is a distributed event streaming platform used for building real-time data pipelines. Key concepts: Topics are categories for messages. Partitions enable parallel processing within a topic. Producers send messages to topics, choosing partitions by key or round-robin. Consumers read messages using consumer groups — each partition is assigned to exactly one consumer in a group. Offsets track consumer position. Consumer lag (difference between latest offset and consumer offset) indicates if consumers are keeping up. Use kafka-consumer-groups.sh to monitor lag.",
                "source": "kafka-guide.md",
                "topic": "kafka",
            },
            {
                "text": "Kafka configuration for Spring Boot: Use spring-kafka dependency. Configure bootstrap-servers in application.yml. Producer config: key-serializer and value-serializer (use JsonSerializer for objects). Consumer config: group-id (required), auto-offset-reset (earliest or latest), enable-auto-commit (false for manual ack recommended). Use @KafkaListener annotation on consumer methods. For error handling, configure a DefaultErrorHandler with BackOff for retry logic. Dead letter topics store messages that fail after all retries.",
                "source": "spring-kafka.md",
                "topic": "kafka",
            },
            {
                "text": "Database connection pooling with HikariCP (Spring Boot default): maximum-pool-size should be set to (2 * CPU cores) + number of disks, typically 10-20 for most applications. connection-timeout is 30 seconds by default — reduce to 5-10 seconds to fail fast. idle-timeout controls how long idle connections are kept (default 10 minutes). max-lifetime should be set lower than your database's wait_timeout (usually 30 minutes). Monitor pool metrics via Spring Boot Actuator /metrics endpoint under hikaricp.* prefix.",
                "source": "hikaricp-tuning.md",
                "topic": "database",
            },
            {
                "text": "PostgreSQL query optimization: Always use EXPLAIN ANALYZE to understand query execution plans. Key indicators: Seq Scan on large tables means a missing index — add one. Nested Loop with high row counts may need a Hash Join — ensure enough work_mem. High actual time on a specific node is your bottleneck. Use pg_stat_statements extension to find the most expensive queries by total_exec_time. Create composite indexes for multi-column WHERE clauses. Use partial indexes for queries that filter on a specific condition (WHERE status = 'active').",
                "source": "postgres-optimization.md",
                "topic": "database",
            },
            {
                "text": "Microservice resilience with Resilience4j: Circuit Breaker has three states — CLOSED (normal, requests pass through), OPEN (failing, requests are rejected immediately with fallback), HALF_OPEN (testing recovery by allowing limited requests). Configure: failureRateThreshold percentage, slidingWindowSize for sample count, waitDurationInOpenState before trying HALF_OPEN. Combine with Retry (use exponential backoff, set maxAttempts), Bulkhead (limit concurrent calls to protect resources), and TimeLimiter (set timeoutDuration to prevent hanging).",
                "source": "resilience4j.md",
                "topic": "architecture",
            },
            {
                "text": "Docker best practices for Spring Boot: Use multi-stage builds — Stage 1 compiles with Maven/Gradle, Stage 2 uses only the JRE (amazoncorretto:21-alpine) to run the JAR. This reduces image size from ~800MB to ~150MB. Use .dockerignore to exclude target/, .git/, and IDE files. Never run as root — add 'RUN addgroup -S app && adduser -S app -G app' and 'USER app'. Spring Boot layered JARs (spring-boot-maven-plugin with layers enabled) improve Docker cache efficiency by separating dependencies from application code.",
                "source": "docker-spring-boot.md",
                "topic": "devops",
            },
        ]

        total_chunks = 0
        for doc in sample_docs:
            chunks = self.add_document(doc["text"], doc["source"], doc["topic"])
            total_chunks += chunks

        print(f"  📚 Loaded {len(sample_docs)} documents → {total_chunks} chunks indexed")

    # ── Query Reformulation ──

    def reformulate_query(self, user_query: str) -> str:
        """Rewrite follow-up questions into standalone search queries."""
        if len(self.chat_history) < 2:
            return user_query

        history_text = "\n".join(
            f"{msg['role'].upper()}: {msg['content'][:150]}"
            for msg in self.chat_history[-6:]
        )

        response = client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": (
                    "Rewrite the follow-up question into a standalone search query "
                    "that includes all necessary context from the history. "
                    "Return ONLY the rewritten query."
                )},
                {"role": "user", "content": (
                    f"History:\n{history_text}\n\n"
                    f"Follow-up: {user_query}\n\nStandalone query:"
                )}
            ],
            temperature=0,
            max_tokens=100,
        )

        return response.choices[0].message.content.strip()

    # ── Retrieval ──

    def retrieve(self, query: str, n_results: int = 4, topic: str = None) -> list[dict]:
        """Search the knowledge base."""
        where_filter = {"topic": topic} if topic else None

        results = self.collection.query(
            query_texts=[query],
            n_results=n_results,
            where=where_filter,
        )

        retrieved = []
        for i in range(len(results["documents"][0])):
            retrieved.append({
                "text": results["documents"][0][i],
                "source": results["metadatas"][0][i]["source"],
                "topic": results["metadatas"][0][i]["topic"],
                "distance": results["distances"][0][i],
            })

        return retrieved

    # ── Generation ──

    def generate(self, query: str, documents: list[dict]) -> str:
        """Generate answer with context and history."""
        context = "\n\n".join(
            f"[{i+1}] Source: {doc['source']}\n{doc['text']}"
            for i, doc in enumerate(documents)
        )

        messages = [
            {"role": "system", "content": (
                "You are a knowledgeable technical assistant for a Java/Spring Boot team. "
                "Answer based on the provided context documents.\n\n"
                "Rules:\n"
                "1. Use ONLY information from the context documents\n"
                "2. Cite sources using [1], [2], etc. after each claim\n"
                "3. If the context doesn't contain the answer, say: "
                "'I don't have enough information in my knowledge base to answer that.'\n"
                "4. Be concise and practical\n"
                "5. Include code snippets when relevant"
            )}
        ]

        # Add conversation history (last 6 messages)
        for msg in self.chat_history[-6:]:
            messages.append(msg)

        messages.append({
            "role": "user",
            "content": (
                f"Context documents:\n{context}\n\n"
                f"Question: {query}"
            ),
        })

        response = client.chat.completions.create(
            model=MODEL,
            messages=messages,
            temperature=0.1,
            max_tokens=600,
        )

        return response.choices[0].message.content

    # ── Main Chat Method ──

    def chat(self, user_input: str) -> str:
        """
        The complete RAG pipeline:
        1. Reformulate query (if follow-up)
        2. Retrieve relevant documents
        3. Generate cited answer
        4. Update history
        """
        # Step 1: Reformulate
        search_query = self.reformulate_query(user_input)
        if search_query != user_input:
            print(f"    🔄 Reformulated: \"{search_query}\"")

        # Step 2: Retrieve
        documents = self.retrieve(search_query, n_results=4)
        self.sources_used = [d["source"] for d in documents]

        # Step 3: Generate
        answer = self.generate(user_input, documents)

        # Step 4: Update history
        self.chat_history.append({"role": "user", "content": user_input})
        self.chat_history.append({"role": "assistant", "content": answer})

        return answer


# ══════════════════════════════════════════════════════
# INTERACTIVE REPL
# ══════════════════════════════════════════════════════

def main():
    print("╔══════════════════════════════════════════════╗")
    print("║  🤖 RAG Chatbot — Module 3 Project           ║")
    print("║  Ask questions about Spring Boot, Kafka,     ║")
    print("║  PostgreSQL, Docker, and Microservices        ║")
    print("╚══════════════════════════════════════════════╝\n")

    bot = RAGChatbot()
    bot.add_sample_data()

    print(f"\n  💡 Commands:")
    print(f"     /sources  — Show sources used for last answer")
    print(f"     /history  — Show conversation history")
    print(f"     /clear    — Clear conversation history")
    print(f"     /stats    — Show knowledge base stats")
    print(f"     /quit     — Exit\n")

    while True:
        try:
            user_input = input("  👤 You: ").strip()

            if not user_input:
                continue

            if user_input.startswith("/"):
                cmd = user_input.lower()

                if cmd == "/quit":
                    print("\n  👋 Goodbye!\n")
                    break
                elif cmd == "/sources":
                    if bot.sources_used:
                        print(f"\n  📄 Sources used:")
                        for s in set(bot.sources_used):
                            print(f"     • {s}")
                    else:
                        print("  No query made yet.")
                elif cmd == "/history":
                    print(f"\n  📜 History ({len(bot.chat_history)} messages):")
                    for msg in bot.chat_history:
                        role = "👤" if msg["role"] == "user" else "🤖"
                        print(f"     {role} {msg['content'][:80]}...")
                elif cmd == "/clear":
                    bot.chat_history.clear()
                    print("  🗑️  History cleared.")
                elif cmd == "/stats":
                    print(f"\n  📊 Knowledge base: {bot.collection.count()} chunks")
                    print(f"     Chat history: {len(bot.chat_history)} messages")
                else:
                    print(f"  ❓ Unknown command: {cmd}")
                print()
                continue

            # Run RAG pipeline
            answer = bot.chat(user_input)

            print(f"\n  🤖 {answer}")
            print(f"\n    📄 Sources: {', '.join(set(bot.sources_used))}\n")

        except (KeyboardInterrupt, EOFError):
            print("\n\n  👋 Goodbye!\n")
            break
        except Exception as e:
            print(f"\n  ❌ Error: {e}\n")


if __name__ == "__main__":
    main()
