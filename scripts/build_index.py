"""Build embeddings and FAISS index from course data."""

import json
from pathlib import Path

import numpy as np

from src.data.schemas import Course
from src.engine.embedder import Embedder
from src.engine.indexer import build_index, save_index

DATA_DIR = Path("data")
RAW_DIR = DATA_DIR / "raw"
PROCESSED_DIR = DATA_DIR / "processed"


def main() -> None:
    courses_path = RAW_DIR / "courses.json"
    courses = [Course(**c) for c in json.loads(courses_path.read_text(encoding="utf-8"))]

    print(f"Embedding {len(courses)} courses...")
    embedder = Embedder()
    embeddings = embedder.embed_courses(courses)

    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    emb_path = PROCESSED_DIR / "embeddings.npy"
    np.save(str(emb_path), embeddings)
    print(f"Saved embeddings to {emb_path} (shape: {embeddings.shape})")

    index = build_index(embeddings)
    idx_path = PROCESSED_DIR / "faiss.index"
    save_index(index, idx_path)
    print(f"Saved FAISS index to {idx_path} ({index.ntotal} vectors)")


if __name__ == "__main__":
    main()
