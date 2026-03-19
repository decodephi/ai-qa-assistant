# modules/vector_store.py
# Lightweight in-memory vector database using:
#   - sentence-transformers  → create embeddings (free, runs locally)
#   - FAISS                  → fast similarity search (free, by Facebook AI)
#
# No external database server needed. Everything lives in RAM per session.
# Each new query clears the old index and rebuilds — simple, stateless design.

import numpy as np
import faiss
from sentence_transformers import SentenceTransformer

# ── Load embedding model once at module level ─────────────────────────────────
# all-MiniLM-L6-v2 is tiny (~80 MB), very fast, and works great for RAG tasks.
print("[vector_store] Loading embedding model (all-MiniLM-L6-v2)...")
_embedder = SentenceTransformer("all-MiniLM-L6-v2")
print("[vector_store] Embedding model loaded.")

EMBEDDING_DIM = 384   # output dimension of all-MiniLM-L6-v2
TOP_K         = 4     # number of top chunks to retrieve per query


class VectorStore:
    """
    In-memory vector store backed by FAISS flat index (exact search).

    Workflow:
        1. Call build(chunks) after scraping each new query
        2. Call retrieve(query) to get the most relevant chunks
    """

    def __init__(self):
        self._index:  faiss.IndexFlatL2 | None = None  # FAISS index
        self._chunks: list[dict]               = []     # original chunk dicts

    def build(self, chunks: list[dict]) -> None:
        """
        Embed all chunks and store them in the FAISS index.

        Args:
            chunks: List of dicts from chunker.py
                    Each must have at least: {"text": str, "source": str}

        Steps:
            1. Extract raw text from each chunk
            2. Encode all texts into embedding vectors in one batch
            3. Normalise vectors (makes cosine ≈ L2 search)
            4. Build a fresh FAISS flat index and add all vectors
        """
        if not chunks:
            print("[vector_store] No chunks to index.")
            self._index  = None
            self._chunks = []
            return

        self._chunks = chunks

        # Extract text for embedding
        texts = [c["text"] for c in chunks]

        # Encode in one batch — returns numpy array of shape (N, 384)
        print(f"[vector_store] Embedding {len(texts)} chunks...")
        embeddings = _embedder.encode(texts, show_progress_bar=False)
        embeddings = np.array(embeddings, dtype="float32")

        # L2-normalise so that inner product ≈ cosine similarity
        faiss.normalize_L2(embeddings)

        # Build FAISS index (IndexFlatL2 = brute-force exact search)
        self._index = faiss.IndexFlatL2(EMBEDDING_DIM)
        self._index.add(embeddings)

        print(f"[vector_store] Index built with {self._index.ntotal} vectors.")

    def retrieve(self, query: str, top_k: int = TOP_K) -> list[dict]:
        """
        Semantic search: return the top-k most relevant chunks for a query.

        Args:
            query: The user's question (or enhanced query from memory)
            top_k: Number of chunks to return

        Returns:
            List of the top-k chunk dicts (sorted by relevance, best first)
            Returns [] if index is empty.
        """
        if self._index is None or self._index.ntotal == 0:
            print("[vector_store] Index is empty — cannot retrieve.")
            return []

        # Embed the query
        q_vec = _embedder.encode([query], show_progress_bar=False)
        q_vec = np.array(q_vec, dtype="float32")
        faiss.normalize_L2(q_vec)

        # Search — returns distances and indices of nearest neighbours
        k       = min(top_k, self._index.ntotal)
        _, idxs = self._index.search(q_vec, k)

        # Collect matching chunks (filter out FAISS sentinel value -1)
        results = [
            self._chunks[i]
            for i in idxs[0]
            if i != -1
        ]

        print(f"[vector_store] Retrieved {len(results)} relevant chunks.")
        return results

    def clear(self) -> None:
        """Reset the index and chunk store."""
        self._index  = None
        self._chunks = []

    def is_ready(self) -> bool:
        """Return True if the index has been built and contains vectors."""
        return self._index is not None and self._index.ntotal > 0


# ── Module-level singleton ─────────────────────────────────────────────────
# One shared store used across the whole app session.
vector_store = VectorStore()


# if __name__ == "__main__":
#     print("\nTesting VectorStore...\n")

#     sample_chunks = [
#         {"text": "AI is artificial intelligence", "source": "url1"},
#         {"text": "Machine learning is a subset of AI", "source": "url2"},
#         {"text": "Deep learning uses neural networks", "source": "url3"}
#     ]

#     vector_store.build(sample_chunks)

#     results = vector_store.retrieve("What is AI?")

#     print("\nTop Results:\n")
#     for r in results:
#         print(r)