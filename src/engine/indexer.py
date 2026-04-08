"""FAISS index build and load utilities."""

from __future__ import annotations

from pathlib import Path

import faiss
import numpy as np


def build_index(embeddings: np.ndarray) -> faiss.IndexFlatIP:
    """Create a FAISS inner-product index from normalized embeddings."""
    embeddings = embeddings.astype("float32")
    dimension = embeddings.shape[1]
    index = faiss.IndexFlatIP(dimension)
    index.add(embeddings)
    return index


def save_index(index: faiss.IndexFlatIP, path: str | Path) -> None:
    """Write a FAISS index to disk."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    faiss.write_index(index, str(path))


def load_index(path: str | Path) -> faiss.IndexFlatIP:
    """Load a FAISS index from disk."""
    return faiss.read_index(str(path))
