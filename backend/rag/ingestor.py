"""Create embeddings for policy chunks using sentence-transformers."""

import numpy as np
import logging
from typing import List, Dict
try:
    from sentence_transformers import SentenceTransformer
    _ST_AVAILABLE = True
except (ImportError, OSError):
    SentenceTransformer = None
    _ST_AVAILABLE = False


logger = logging.getLogger(__name__)

MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"


class PolicyEmbedder:
    """Create dense embeddings for policy text chunks."""

    _model = None

    @classmethod
    def get_model(cls):
        if cls._model is None and _ST_AVAILABLE:
            logger.info(f"Loading sentence transformer: {MODEL_NAME}")
            cls._model = SentenceTransformer(MODEL_NAME)
        return cls._model


    @classmethod
    def embed_chunks(cls, chunks: List[Dict]) -> np.ndarray:
        """
        Create embeddings for all chunks.

        Args:
            chunks: List of chunk dicts with "text" key

        Returns:
            numpy array of shape (n_chunks, embedding_dim)
        """
        model = cls.get_model()
        texts = [chunk["text"] for chunk in chunks]
        embeddings = model.encode(texts, show_progress_bar=True, batch_size=32)
        logger.info(f"Created embeddings: shape={embeddings.shape}")
        return embeddings

    @classmethod
    def embed_query(cls, query: str) -> np.ndarray:
        """Embed a single query string."""
        model = cls.get_model()
        return model.encode([query])[0]