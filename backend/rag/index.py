"""
FAISS index management for policy RAG.
"""

import pickle
import os
import numpy as np
import logging
from typing import Tuple, Optional, List, Dict

try:
    import faiss
    _FAISS_AVAILABLE = True
except ImportError:
    faiss = None
    _FAISS_AVAILABLE = False

logger = logging.getLogger(__name__)


class FAISSIndex:
    """Manage FAISS index creation and loading."""

    @staticmethod
    def build(embeddings: np.ndarray, chunks: List[Dict], index_path: str, chunks_path: str):
        """Build and save a FAISS index."""
        dimension = embeddings.shape[1]
        index = faiss.IndexFlatIP(dimension)
        index.add(embeddings.astype(np.float32))

        os.makedirs(os.path.dirname(index_path), exist_ok=True)
        faiss.write_index(index, index_path)

        with open(chunks_path, "wb") as f:
            pickle.dump(chunks, f)

        logger.info(f"Built FAISS index: {index.ntotal} vectors, dimension {dimension}")
        return index, chunks

    @staticmethod
    def load(index_path: str, chunks_path: str) -> Tuple[Optional[faiss.Index], Optional[List[Dict]]]:
        """Load a FAISS index and associated chunks."""
        if not os.path.exists(index_path):
            logger.warning(f"FAISS index file not found: {index_path}")
            return None, None

        if not os.path.exists(chunks_path):
            logger.warning(f"Chunks file not found: {chunks_path}")
            return None, None

        index = faiss.read_index(index_path)
        with open(chunks_path, "rb") as f:
            chunks = pickle.load(f)

        logger.info(f"Loaded FAISS index: {index.ntotal} vectors")
        return index, chunks