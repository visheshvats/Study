#!/usr/bin/env python3
"""
RAG Pipeline — Query → Retrieval → Context Compilation → Generation
=====================================================================
A functional end-to-end Retrieval-Augmented Generation execution loop that:

  1. Accepts a user query
  2. Embeds the query into a dense vector
  3. Searches a mock vector store for relevant document chunks
  4. Compiles retrieved context into a structured prompt
  5. Passes the augmented prompt to a mock LLM for generation

Run:
    python rag_pipeline.py
"""

import math
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple


# ── Data Structures ─────────────────────────────────────────────────────────
@dataclass
class DocumentChunk:
    """A chunk of a source document with its embedding."""
    doc_id: str
    chunk_index: int
    text: str
    source: str
    embedding: List[float]
    metadata: Dict[str, str] = field(default_factory=dict)

    @property
    def chunk_id(self) -> str:
        return f"{self.doc_id}:chunk_{self.chunk_index}"


@dataclass
class RetrievalResult:
    """A single search result with relevance score."""
    chunk: DocumentChunk
    score: float
    rank: int


@dataclass
class RAGResponse:
    """The final response including provenance tracking."""
    answer: str
    sources: List[RetrievalResult]
    prompt_tokens: int
    context_tokens: int


# ── Mock Embedding Function ────────────────────────────────────────────────
# In production, this would call an embedding API (OpenAI, Cohere, etc.)
KEYWORD_VECTORS: Dict[str, List[float]] = {
    "payment":     [0.90, 0.10, 0.05, 0.85, 0.08, 0.12, 0.03, 0.92],
    "refund":      [0.88, 0.12, 0.07, 0.82, 0.10, 0.15, 0.05, 0.90],
    "billing":     [0.85, 0.15, 0.10, 0.80, 0.12, 0.18, 0.08, 0.87],
    "account":     [0.70, 0.30, 0.20, 0.65, 0.25, 0.30, 0.15, 0.72],
    "shipping":    [0.20, 0.80, 0.75, 0.15, 0.82, 0.10, 0.70, 0.18],
    "delivery":    [0.22, 0.78, 0.72, 0.18, 0.80, 0.12, 0.68, 0.20],
    "tracking":    [0.25, 0.75, 0.70, 0.20, 0.78, 0.15, 0.65, 0.22],
    "return":      [0.60, 0.40, 0.35, 0.55, 0.45, 0.38, 0.30, 0.58],
    "warranty":    [0.50, 0.50, 0.45, 0.48, 0.52, 0.42, 0.40, 0.50],
    "cancel":      [0.82, 0.18, 0.12, 0.78, 0.15, 0.20, 0.10, 0.85],
    "password":    [0.15, 0.25, 0.85, 0.10, 0.20, 0.88, 0.80, 0.12],
    "login":       [0.18, 0.22, 0.82, 0.12, 0.18, 0.85, 0.78, 0.15],
    "error":       [0.40, 0.45, 0.60, 0.38, 0.42, 0.55, 0.58, 0.42],
    "help":        [0.50, 0.50, 0.50, 0.50, 0.50, 0.50, 0.50, 0.50],
}


def embed_query(text: str) -> List[float]:
    """
    Generate a mock embedding by averaging keyword vectors found in the text.
    Production systems use dense encoder models (e.g., text-embedding-3-small).
    """
    words = text.lower().split()
    matched = [KEYWORD_VECTORS[w] for w in words if w in KEYWORD_VECTORS]
    if not matched:
        return [0.5] * 8  # Neutral fallback
    dim = len(matched[0])
    avg = [sum(m[i] for m in matched) / len(matched) for i in range(dim)]
    return avg


# ── Vector Store (Mock) ────────────────────────────────────────────────────
class VectorStore:
    """In-memory vector store simulating a production vector database."""

    def __init__(self):
        self._chunks: List[DocumentChunk] = []

    def add_chunks(self, chunks: List[DocumentChunk]) -> int:
        self._chunks.extend(chunks)
        return len(self._chunks)

    def search(
        self,
        query_embedding: List[float],
        top_k: int = 3,
        score_threshold: float = 0.0,
    ) -> List[RetrievalResult]:
        """Cosine similarity search over all stored chunks."""
        results: List[Tuple[DocumentChunk, float]] = []
        for chunk in self._chunks:
            score = self._cosine_similarity(query_embedding, chunk.embedding)
            if score >= score_threshold:
                results.append((chunk, score))
        results.sort(key=lambda x: x[1], reverse=True)
        return [
            RetrievalResult(chunk=c, score=s, rank=i + 1)
            for i, (c, s) in enumerate(results[:top_k])
        ]

    @staticmethod
    def _cosine_similarity(a: List[float], b: List[float]) -> float:
        dot = sum(x * y for x, y in zip(a, b))
        mag_a = math.sqrt(sum(x * x for x in a))
        mag_b = math.sqrt(sum(x * x for x in b))
        if mag_a == 0 or mag_b == 0:
            return 0.0
        return dot / (mag_a * mag_b)


# ── Context Compiler ───────────────────────────────────────────────────────
class ContextCompiler:
    """Assembles retrieved chunks into a structured prompt context block."""

    SYSTEM_TEMPLATE = (
        "You are a helpful customer support assistant. Answer the user's "
        "question based ONLY on the provided context documents. If the context "
        "does not contain enough information, say so explicitly.\n\n"
        "## Retrieved Context\n{context}\n\n"
        "## User Question\n{query}\n\n"
        "## Answer"
    )

    def compile(
        self,
        query: str,
        results: List[RetrievalResult],
        max_context_tokens: int = 1500,
    ) -> Tuple[str, int]:
        """Build the augmented prompt, respecting token limits."""
        context_blocks: List[str] = []
        token_count = 0

        for r in results:
            chunk_text = (
                f"[Source: {r.chunk.source} | Relevance: {r.score:.4f}]\n"
                f"{r.chunk.text}"
            )
            chunk_tokens = len(chunk_text) // 4  # Rough estimate
            if token_count + chunk_tokens > max_context_tokens:
                break
            context_blocks.append(chunk_text)
            token_count += chunk_tokens

        context = "\n\n---\n\n".join(context_blocks)
        prompt = self.SYSTEM_TEMPLATE.format(context=context, query=query)
        return prompt, token_count


# ── Mock LLM ───────────────────────────────────────────────────────────────
class MockLLM:
    """Simulates an LLM response by extracting key phrases from context."""

    def generate(self, prompt: str) -> str:
        # Extract the context section
        if "## Retrieved Context" in prompt and "## User Question" in prompt:
            context = prompt.split("## Retrieved Context")[1].split("## User Question")[0]
            question = prompt.split("## User Question")[1].split("## Answer")[0].strip()

            # Simple extractive "generation"
            sentences = [s.strip() for s in context.replace("\n", " ").split(".") if len(s.strip()) > 20]
            if sentences:
                summary = ". ".join(sentences[:3]) + "."
                return f"Based on the retrieved documentation: {summary}"

        return "I could not find sufficient information in the provided context to answer your question."


# ── RAG Pipeline Orchestrator ──────────────────────────────────────────────
class RAGPipeline:
    """End-to-end RAG orchestration: embed → retrieve → compile → generate."""

    def __init__(
        self,
        vector_store: VectorStore,
        context_compiler: ContextCompiler,
        llm: MockLLM,
        top_k: int = 3,
        score_threshold: float = 0.5,
    ):
        self.vector_store = vector_store
        self.context_compiler = context_compiler
        self.llm = llm
        self.top_k = top_k
        self.score_threshold = score_threshold

    def query(self, user_query: str) -> RAGResponse:
        """Execute the full RAG pipeline."""
        # Step 1: Embed query
        query_vec = embed_query(user_query)

        # Step 2: Retrieve relevant chunks
        results = self.vector_store.search(
            query_vec, top_k=self.top_k, score_threshold=self.score_threshold
        )

        # Step 3: Compile context prompt
        prompt, context_tokens = self.context_compiler.compile(user_query, results)

        # Step 4: Generate response
        answer = self.llm.generate(prompt)

        return RAGResponse(
            answer=answer,
            sources=results,
            prompt_tokens=len(prompt) // 4,
            context_tokens=context_tokens,
        )


# ── Demo ────────────────────────────────────────────────────────────────────
def build_knowledge_base() -> VectorStore:
    """Populate the vector store with mock customer support documents."""
    store = VectorStore()

    documents = [
        DocumentChunk(
            doc_id="FAQ-001", chunk_index=0,
            text="To request a refund, navigate to Orders > Select Order > Request Refund. "
                 "Refunds are processed within 5-7 business days. The refund amount will be "
                 "credited to your original payment method.",
            source="FAQ: Refunds & Returns",
            embedding=embed_query("refund payment request process"),
        ),
        DocumentChunk(
            doc_id="FAQ-002", chunk_index=0,
            text="If your payment was declined, verify your card details and ensure sufficient "
                 "balance. Common error codes: E-4001 (insufficient funds), E-4002 (expired card), "
                 "E-4003 (incorrect CVV). Contact your bank if the issue persists.",
            source="FAQ: Payment Issues",
            embedding=embed_query("payment error billing declined"),
        ),
        DocumentChunk(
            doc_id="FAQ-003", chunk_index=0,
            text="Track your order using the tracking number sent to your email. Standard shipping "
                 "takes 5-8 business days. Express shipping takes 2-3 business days. "
                 "International orders may take 10-15 business days.",
            source="FAQ: Shipping & Delivery",
            embedding=embed_query("shipping delivery tracking order"),
        ),
        DocumentChunk(
            doc_id="FAQ-004", chunk_index=0,
            text="To reset your password, click 'Forgot Password' on the login page. "
                 "Enter your registered email address. A reset link will be sent within 5 minutes. "
                 "The link expires after 24 hours.",
            source="FAQ: Account Management",
            embedding=embed_query("password login account reset"),
        ),
        DocumentChunk(
            doc_id="FAQ-005", chunk_index=0,
            text="To cancel an order, go to Orders > Select Order > Cancel Order. "
                 "Orders can only be cancelled before they ship. Once shipped, you must "
                 "initiate a return instead. Cancellation refunds process within 3 business days.",
            source="FAQ: Order Cancellation",
            embedding=embed_query("cancel order refund payment"),
        ),
        DocumentChunk(
            doc_id="POLICY-001", chunk_index=0,
            text="Our warranty covers manufacturing defects for 12 months from the date of purchase. "
                 "Normal wear and tear, accidental damage, and unauthorized modifications are excluded. "
                 "File a warranty claim at support.example.com/warranty.",
            source="Policy: Warranty Terms",
            embedding=embed_query("warranty return policy"),
        ),
    ]

    count = store.add_chunks(documents)
    return store


def run_demo() -> None:
    print("=" * 72)
    print("RAG PIPELINE — Retrieval-Augmented Generation Demo")
    print("=" * 72)

    # Build components
    store = build_knowledge_base()
    compiler = ContextCompiler()
    llm = MockLLM()
    pipeline = RAGPipeline(store, compiler, llm, top_k=3, score_threshold=0.3)

    # Test queries
    queries = [
        "How do I get a refund for my order?",
        "My payment keeps getting declined, what should I do?",
        "How long does shipping take for international orders?",
        "I forgot my password and can't login",
    ]

    for query in queries:
        print(f"\n{'─' * 60}")
        print(f"  USER QUERY: {query}")
        print(f"{'─' * 60}")

        response = pipeline.query(query)

        print(f"\n  RETRIEVED SOURCES:")
        for r in response.sources:
            print(f"    #{r.rank} [{r.score:.4f}] {r.chunk.source}")
            print(f"       {r.chunk.text[:80]}...")

        print(f"\n  GENERATED ANSWER:")
        print(f"    {response.answer[:200]}...")

        print(f"\n  TOKEN USAGE:")
        print(f"    Context tokens : {response.context_tokens}")
        print(f"    Total prompt   : {response.prompt_tokens}")

    # Pipeline architecture summary
    print(f"\n{'═' * 72}")
    print("  RAG PIPELINE ARCHITECTURE:")
    print("  ┌──────────┐   ┌───────────┐   ┌──────────────┐   ┌─────────┐")
    print("  │  User    │──▶│ Embedding │──▶│ Vector Store │──▶│ Context │")
    print("  │  Query   │   │  Model    │   │  (ANN Search)│   │Compiler │")
    print("  └──────────┘   └───────────┘   └──────────────┘   └────┬────┘")
    print("                                                         │")
    print("  ┌──────────┐                                    ┌──────▼─────┐")
    print("  │ Response │◀───────────────────────────────────│    LLM     │")
    print("  │ + Sources│                                    │ Generation │")
    print("  └──────────┘                                    └────────────┘")
    print("═" * 72)


if __name__ == "__main__":
    run_demo()
