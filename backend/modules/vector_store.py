# backend/modules/vector_store.py
# In-memory vector store using FAISS + sentence-transformers.

import logging
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer

logger = logging.getLogger(__name__)

EMBEDDING_DIM = 384
TOP_K         = 6

logger.info("[vector_store] Loading embedding model (all-MiniLM-L6-v2)…")
_embedder = SentenceTransformer("all-MiniLM-L6-v2")
logger.info("[vector_store] Embedding model loaded.")


class VectorStore:
    """
    In-memory FAISS vector store.

    Workflow:
        1. build(chunks)   — embed and index all chunks for a query
        2. retrieve(query) — semantic search for the top-k most relevant chunks
    """

    def __init__(self):
        self._index:  faiss.IndexFlatL2 | None = None
        self._chunks: list[dict] = []

    def build(self, chunks: list[dict]) -> None:
        """
        Embed all chunks and store them in the FAISS index.

        Args:
            chunks: List of dicts, each with at least {"text": str, "source": str}
        """
        if not chunks:
            logger.warning("[vector_store] No chunks to index.")
            self._index  = None
            self._chunks = []
            return

        self._chunks = chunks
        texts        = [c["text"] for c in chunks]

        logger.info("[vector_store] Embedding %d chunks…", len(texts))
        embeddings = _embedder.encode(texts, show_progress_bar=False)
        embeddings = np.array(embeddings, dtype="float32")
        faiss.normalize_L2(embeddings)

        self._index = faiss.IndexFlatL2(EMBEDDING_DIM)
        self._index.add(embeddings)
        logger.info("[vector_store] Index built with %d vectors.", self._index.ntotal)

    def retrieve(self, query: str, top_k: int = TOP_K) -> list[dict]:
        """
        Semantic search: return the top-k most relevant chunks.

        Args:
            query:  The user question (or enhanced query from memory)
            top_k:  Number of chunks to return

        Returns:
            List of chunk dicts sorted by relevance (best first).
        """
        if self._index is None or self._index.ntotal == 0:
            logger.warning("[vector_store] Index is empty — cannot retrieve.")
            return []

        q_vec = _embedder.encode([query], show_progress_bar=False)
        q_vec = np.array(q_vec, dtype="float32")
        faiss.normalize_L2(q_vec)

        k = min(top_k, self._index.ntotal)
        _, idxs = self._index.search(q_vec, k)

        results = [
            self._chunks[i]
            for i in idxs[0]
            if i != -1 and i < len(self._chunks)
        ]
        # Filter out very short chunks (noise)
        results = [c for c in results if len(c.get("text", "")) > 50]

        logger.info("[vector_store] Retrieved %d relevant chunks.", len(results))
        return results

    def clear(self) -> None:
        """Reset the index and chunk store."""
        self._index  = None
        self._chunks = []

    def is_ready(self) -> bool:
        """Return True if the index has been built and contains vectors."""
        return self._index is not None and self._index.ntotal > 0


# Singleton
vector_store = VectorStore()
