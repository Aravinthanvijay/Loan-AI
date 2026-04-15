"""
Policy embedder — generates embeddings for policy text using sentence-transformers.
"""

import numpy as np
import logging
from typing import Optional

logger = logging.getLogger(__name__)

_model = None


def _get_model():
    """Lazy load the sentence-transformer model."""
    global _model
    if _model is None:
        try:
            from sentence_transformers import SentenceTransformer
            _model = SentenceTransformer("all-MiniLM-L6-v2")
            logger.info("Loaded sentence-transformer model: all-MiniLM-L6-v2")
        except (ImportError, OSError) as e:
            logger.warning(f"sentence-transformers unavailable (DLL/import error). Using random fallback. Error: {e}")
        except Exception as e:
            logger.error(f"Failed to load sentence-transformer: {e}")
    return _model


class PolicyEmbedder:
    """Generate embeddings for policy text queries."""

    @staticmethod
    def embed_query(query: str) -> np.ndarray:
        """
        Embed a single query string.

        Args:
            query: Natural language query

        Returns:
            Normalized embedding vector (384-dim for all-MiniLM-L6-v2)
        """
        model = _get_model()
        if model is not None:
            embedding = model.encode(query, normalize_embeddings=True)
            return np.array(embedding).astype(np.float32)
        else:
            # Fallback: random embedding for demo
            logger.warning("Using random embedding fallback")
            vec = np.random.rand(384).astype(np.float32)
            vec = vec / np.linalg.norm(vec)
            return vec

    @staticmethod
    def embed_texts(texts: list) -> np.ndarray:
        """
        Embed a list of text strings.

        Args:
            texts: List of strings to embed

        Returns:
            Array of normalized embeddings (N x 384)
        """
        model = _get_model()
        if model is not None:
            embeddings = model.encode(texts, normalize_embeddings=True, show_progress_bar=False)
            return np.array(embeddings).astype(np.float32)
        else:
            logger.warning("Using random embeddings fallback")
            vecs = np.random.rand(len(texts), 384).astype(np.float32)
            norms = np.linalg.norm(vecs, axis=1, keepdims=True)
            return vecs / norms
