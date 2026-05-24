#!/usr/bin/env python3
"""
Vector Database Client — Mock HNSW Graph Similarity Search
============================================================
Simulates a production vector database client that performs approximate
nearest-neighbour (ANN) search using a simplified Hierarchical Navigable
Small World (HNSW) graph structure.

Covers:
  • HNSW graph construction with configurable layers
  • Greedy beam search traversal
  • Cosine & Euclidean distance metrics
  • Index statistics and performance profiling

Run:
    python vector_db_client.py
"""

import math
import random
import time
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set, Tuple

random.seed(42)


# ── Data Types ──────────────────────────────────────────────────────────────
Vector = List[float]


@dataclass
class VectorRecord:
    """A stored vector with its associated metadata."""
    id: str
    vector: Vector
    payload: Dict[str, str] = field(default_factory=dict)


@dataclass
class SearchResult:
    """A single ANN search result."""
    record: VectorRecord
    distance: float
    hops: int = 0


# ── Distance Functions ─────────────────────────────────────────────────────
def cosine_distance(a: Vector, b: Vector) -> float:
    """1 - cosine_similarity (lower = more similar)."""
    dot = sum(x * y for x, y in zip(a, b))
    mag_a = math.sqrt(sum(x * x for x in a))
    mag_b = math.sqrt(sum(x * x for x in b))
    if mag_a == 0 or mag_b == 0:
        return 1.0
    return 1.0 - dot / (mag_a * mag_b)


def euclidean_distance(a: Vector, b: Vector) -> float:
    return math.sqrt(sum((x - y) ** 2 for x, y in zip(a, b)))


DISTANCE_FUNCTIONS = {
    "cosine": cosine_distance,
    "euclidean": euclidean_distance,
}


# ── HNSW Layer ──────────────────────────────────────────────────────────────
@dataclass
class HNSWNode:
    """A node in a single HNSW layer."""
    record: VectorRecord
    neighbors: List[str] = field(default_factory=list)  # neighbor IDs


class HNSWLayer:
    """A single layer of the HNSW graph."""

    def __init__(self, max_neighbors: int = 8):
        self.max_neighbors = max_neighbors
        self.nodes: Dict[str, HNSWNode] = {}

    def add_node(self, record: VectorRecord, dist_fn) -> None:
        node = HNSWNode(record=record)

        if self.nodes:
            # Find closest existing nodes
            distances = [
                (nid, dist_fn(record.vector, n.record.vector))
                for nid, n in self.nodes.items()
            ]
            distances.sort(key=lambda x: x[1])

            # Connect to top-M closest nodes
            for nid, _ in distances[: self.max_neighbors]:
                node.neighbors.append(nid)
                # Bidirectional connection
                self.nodes[nid].neighbors.append(record.id)
                # Prune if over limit
                if len(self.nodes[nid].neighbors) > self.max_neighbors:
                    self._prune_neighbors(nid, dist_fn)

        self.nodes[record.id] = node

    def _prune_neighbors(self, node_id: str, dist_fn) -> None:
        """Keep only the M closest neighbors."""
        node = self.nodes[node_id]
        if len(node.neighbors) <= self.max_neighbors:
            return
        distances = [
            (nid, dist_fn(node.record.vector, self.nodes[nid].record.vector))
            for nid in node.neighbors
            if nid in self.nodes
        ]
        distances.sort(key=lambda x: x[1])
        node.neighbors = [nid for nid, _ in distances[: self.max_neighbors]]


# ── HNSW Index ──────────────────────────────────────────────────────────────
class HNSWIndex:
    """
    Simplified HNSW (Hierarchical Navigable Small World) index.

    Structural overview:
      Layer 2 (sparse)  :  few nodes, long-range connections
      Layer 1 (medium)  :  more nodes, medium-range connections
      Layer 0 (dense)   :  ALL nodes, fine-grained connections

    Search: enter at top layer → greedy descend → exhaustive at layer 0.
    """

    def __init__(
        self,
        metric: str = "cosine",
        max_neighbors: int = 8,
        num_layers: int = 3,
        level_probability: float = 0.3,
    ):
        self.dist_fn = DISTANCE_FUNCTIONS[metric]
        self.metric = metric
        self.num_layers = num_layers
        self.level_probability = level_probability
        self.layers = [HNSWLayer(max_neighbors) for _ in range(num_layers)]
        self._records: Dict[str, VectorRecord] = {}
        self._entry_point: Optional[str] = None

    def insert(self, record: VectorRecord) -> None:
        """Insert a vector into the index."""
        self._records[record.id] = record

        # Always insert into layer 0
        self.layers[0].add_node(record, self.dist_fn)

        # Probabilistically insert into higher layers
        for layer_idx in range(1, self.num_layers):
            if random.random() < self.level_probability:
                self.layers[layer_idx].add_node(record, self.dist_fn)
            else:
                break

        if self._entry_point is None:
            self._entry_point = record.id

    def search(self, query: Vector, top_k: int = 5, ef_search: int = 20) -> List[SearchResult]:
        """
        HNSW search: start at the top layer, greedily descend, then
        exhaustively search the bottom layer with an expanded candidate set.
        """
        if not self._records:
            return []

        total_hops = 0

        # Phase 1: Greedy descent through upper layers
        current_best = self._entry_point
        for layer_idx in range(self.num_layers - 1, 0, -1):
            layer = self.layers[layer_idx]
            if current_best not in layer.nodes:
                continue
            current_best, hops = self._greedy_search_layer(
                query, current_best, layer, max_steps=10
            )
            total_hops += hops

        # Phase 2: Exhaustive search on layer 0
        results, hops = self._beam_search_layer(
            query, current_best, self.layers[0], ef_search
        )
        total_hops += hops

        # Return top-k
        results.sort(key=lambda r: r.distance)
        for i, r in enumerate(results[:top_k]):
            r.hops = total_hops
        return results[:top_k]

    def _greedy_search_layer(
        self, query: Vector, entry: str, layer: HNSWLayer, max_steps: int
    ) -> Tuple[str, int]:
        """Greedy walk: always move to the closest unvisited neighbor."""
        current = entry
        current_dist = self.dist_fn(query, layer.nodes[current].record.vector)
        hops = 0
        for _ in range(max_steps):
            improved = False
            for nid in layer.nodes[current].neighbors:
                if nid not in layer.nodes:
                    continue
                d = self.dist_fn(query, layer.nodes[nid].record.vector)
                hops += 1
                if d < current_dist:
                    current = nid
                    current_dist = d
                    improved = True
            if not improved:
                break
        return current, hops

    def _beam_search_layer(
        self, query: Vector, entry: str, layer: HNSWLayer, ef: int
    ) -> Tuple[List[SearchResult], int]:
        """Beam search with expanded candidate set (ef > k)."""
        visited: Set[str] = {entry}
        candidates: List[Tuple[float, str]] = []
        entry_dist = self.dist_fn(query, layer.nodes[entry].record.vector)
        candidates.append((entry_dist, entry))
        results: List[SearchResult] = [
            SearchResult(record=layer.nodes[entry].record, distance=entry_dist)
        ]
        hops = 0

        while candidates:
            candidates.sort(key=lambda x: x[0])
            _, current = candidates.pop(0)

            for nid in layer.nodes[current].neighbors:
                if nid in visited or nid not in layer.nodes:
                    continue
                visited.add(nid)
                hops += 1
                d = self.dist_fn(query, layer.nodes[nid].record.vector)
                results.append(
                    SearchResult(record=layer.nodes[nid].record, distance=d)
                )
                candidates.append((d, nid))

                if len(visited) >= ef:
                    return results, hops

        return results, hops

    def stats(self) -> Dict[str, int]:
        return {
            "total_records": len(self._records),
            "layers": self.num_layers,
            **{f"layer_{i}_nodes": len(self.layers[i].nodes) for i in range(self.num_layers)},
        }


# ── Client Wrapper ──────────────────────────────────────────────────────────
class VectorDBClient:
    """High-level client wrapping the HNSW index (simulates a DB client SDK)."""

    def __init__(self, collection_name: str, metric: str = "cosine"):
        self.collection_name = collection_name
        self.index = HNSWIndex(metric=metric)
        self._insert_count = 0

    def upsert(self, id: str, vector: Vector, payload: Optional[Dict[str, str]] = None) -> None:
        record = VectorRecord(id=id, vector=vector, payload=payload or {})
        self.index.insert(record)
        self._insert_count += 1

    def query(self, vector: Vector, top_k: int = 5) -> List[SearchResult]:
        return self.index.search(vector, top_k=top_k)

    def info(self) -> Dict:
        return {
            "collection": self.collection_name,
            "metric": self.index.metric,
            **self.index.stats(),
        }


# ── Demo ────────────────────────────────────────────────────────────────────
def generate_cluster_vectors(
    center: Vector, count: int, noise: float = 0.08
) -> List[Vector]:
    """Generate vectors clustered around a center point."""
    vectors = []
    for _ in range(count):
        vec = [c + random.gauss(0, noise) for c in center]
        vectors.append(vec)
    return vectors


def run_demo() -> None:
    print("=" * 72)
    print("VECTOR DB CLIENT — HNSW Approximate Nearest Neighbour Search")
    print("=" * 72)

    client = VectorDBClient("customer_support", metric="cosine")

    # Define semantic clusters
    clusters = {
        "payment_issues": {
            "center": [0.90, 0.10, 0.05, 0.85, 0.08, 0.12, 0.03, 0.92],
            "docs": [
                "Payment declined error E-4001",
                "Credit card charge failed",
                "Billing dispute resolution steps",
                "Payment method update guide",
                "Refund processing timeline",
            ],
        },
        "shipping_tracking": {
            "center": [0.10, 0.90, 0.85, 0.08, 0.92, 0.05, 0.88, 0.12],
            "docs": [
                "Standard shipping 5-8 business days",
                "Express delivery tracking info",
                "International shipping customs",
                "Package lost claim process",
                "Delivery address change policy",
            ],
        },
        "account_security": {
            "center": [0.15, 0.20, 0.90, 0.12, 0.18, 0.92, 0.85, 0.10],
            "docs": [
                "Password reset instructions",
                "Two-factor authentication setup",
                "Account locked troubleshooting",
                "Suspicious activity alert",
                "Login history review",
            ],
        },
    }

    # Insert documents
    print("\n  Inserting documents into HNSW index...")
    for cluster_name, cluster_data in clusters.items():
        vectors = generate_cluster_vectors(cluster_data["center"], len(cluster_data["docs"]))
        for i, (doc, vec) in enumerate(zip(cluster_data["docs"], vectors)):
            client.upsert(
                id=f"{cluster_name}_{i}",
                vector=vec,
                payload={"text": doc, "cluster": cluster_name},
            )
    print(f"  Index info: {client.info()}")

    # Query examples
    queries = [
        ("My payment keeps failing",     [0.88, 0.12, 0.08, 0.82, 0.10, 0.15, 0.05, 0.90]),
        ("Where is my package?",          [0.12, 0.88, 0.82, 0.10, 0.90, 0.08, 0.85, 0.15]),
        ("I can't log into my account",   [0.18, 0.22, 0.88, 0.15, 0.20, 0.90, 0.82, 0.12]),
    ]

    for query_text, query_vec in queries:
        print(f"\n{'─' * 60}")
        print(f"  QUERY: \"{query_text}\"")
        print(f"{'─' * 60}")

        start = time.perf_counter()
        results = client.query(query_vec, top_k=3)
        elapsed_us = (time.perf_counter() - start) * 1_000_000

        for r in results:
            print(f"    #{r.hops} hops | dist={r.distance:.4f} | {r.record.payload.get('text', '')}")
            print(f"           cluster: {r.record.payload.get('cluster', 'N/A')}")
        print(f"    ⏱  Search latency: {elapsed_us:.0f}µs")

    # Architecture summary
    print(f"\n{'═' * 72}")
    print("  HNSW ARCHITECTURE:")
    print("  Layer 2 (sparse)  → 3-5 nodes  → long-range navigation jumps")
    print("  Layer 1 (medium)  → 8-12 nodes → mid-range refinement")
    print("  Layer 0 (dense)   → ALL nodes  → precise local search")
    print("")
    print("  Search path: Enter L2 → greedy descend → beam search L0")
    print("  Complexity: O(log N) average vs O(N) brute force")
    print("═" * 72)


if __name__ == "__main__":
    run_demo()
