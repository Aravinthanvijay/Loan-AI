"""Cache management for RAG embeddings."""

import os
import pickle
import logging
from typing import Optional

logger = logging.getLogger(__name__)


class EmbeddingCache:
    """Simple file-based cache for embeddings."""

    @staticmethod
    def save(data, cache_path: str):
        os.makedirs(os.path.dirname(cache_path), exist_ok=True)
        with open(cache_path, "wb") as f:
            pickle.dump(data, f)
        logger.info(f"Cached embeddings to {cache_path}")

    @staticmethod
    def load(cache_path: str) -> Optional[object]:
        if os.path.exists(cache_path):
            with open(cache_path, "rb") as f:
                return pickle.load(f)
        return None

    @staticmethod
    def exists(cache_path: str) -> bool:
        return os.path.exists(cache_path)