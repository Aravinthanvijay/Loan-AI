"""
Policy retriever — searches FAISS index for relevant policy clauses.
"""

import numpy as np
import pickle
import logging
from typing import List, Dict, Optional

from backend.config import settings
from backend.rag.embedder import PolicyEmbedder

logger = logging.getLogger(__name__)


class PolicyRetriever:
    """Retrieve relevant policy clauses using FAISS similarity search."""

    _index = None
    _chunks = None

    @classmethod
    def load_index(cls):
        """Load FAISS index and chunks."""
        try:
            import faiss
            import os

            index_path = settings.FAISS_INDEX_PATH
            chunks_path = settings.EMBEDDINGS_PATH

            if not os.path.exists(index_path) or not os.path.exists(chunks_path):
                logger.warning(
                    f"FAISS index not found at {index_path}. "
                    "Run 'python scripts/build_index.py' first. Using fallback."
                )
                return

            cls._index = faiss.read_index(index_path)
            with open(chunks_path, "rb") as f:
                cls._chunks = pickle.load(f)

            logger.info(f"Loaded FAISS index: {cls._index.ntotal} vectors, {len(cls._chunks)} chunks")

        except ImportError:
            logger.error("faiss-cpu not installed. Run: pip install faiss-cpu")
        except Exception as e:
            logger.error(f"Failed to load FAISS index: {e}")

    @classmethod
    def search(cls, query: str, top_k: int = 3) -> List[Dict]:
        """
        Search for relevant policy clauses.

        Args:
            query: Natural language query
            top_k: Number of results to return

        Returns:
            List of relevant policy chunks with similarity scores
        """
        if cls._index is None:
            cls.load_index()

        if cls._index is None or cls._chunks is None:
            logger.warning("FAISS index not available, returning default policy guidance")
            return cls._get_fallback_policy(query)

        # Embed query
        query_embedding = PolicyEmbedder.embed_query(query)
        query_embedding = query_embedding.reshape(1, -1).astype(np.float32)

        # Search
        distances, indices = cls._index.search(query_embedding, min(top_k, cls._index.ntotal))

        results = []
        for dist, idx in zip(distances[0], indices[0]):
            if 0 <= idx < len(cls._chunks):
                chunk = cls._chunks[idx].copy()
                chunk["similarity_score"] = round(float(dist), 4)
                results.append(chunk)

        return results

    @staticmethod
    def _get_fallback_policy(query: str) -> List[Dict]:
        """Return hardcoded policy guidance when FAISS index is unavailable."""
        query_lower = query.lower()

        policies = []

        if "age" in query_lower:
            policies.append({
                "text": "Minimum age: 21 years. Maximum age at maturity: 65 years. Applicants below 25 require additional verification.",
                "chunk_id": -1,
                "similarity_score": 0.9,
            })

        if "income" in query_lower or "foir" in query_lower:
            policies.append({
                "text": "Minimum monthly income: Rs 15,000 (salaried), Rs 20,000 (self-employed). Maximum FOIR: 50%. FOIR below 30% is healthy.",
                "chunk_id": -2,
                "similarity_score": 0.9,
            })

        if "bureau" in query_lower or "score" in query_lower or "credit" in query_lower:
            policies.append({
                "text": "Minimum bureau score: 650. Score 750+ qualifies for preferential rates. Below 550 triggers auto-reject.",
                "chunk_id": -3,
                "similarity_score": 0.9,
            })

        if "document" in query_lower or "pan" in query_lower or "ocr" in query_lower:
            policies.append({
                "text": "PAN name must match application (80% fuzzy match). Salary slip within 10% of declared income. OCR confidence minimum: 70%.",
                "chunk_id": -4,
                "similarity_score": 0.85,
            })

        if not policies:
            policies.append({
                "text": "Standard underwriting: verify age 21-65, income >= 15K, FOIR <= 50%, bureau >= 650, valid documents.",
                "chunk_id": -5,
                "similarity_score": 0.7,
            })

        return policies[:3]