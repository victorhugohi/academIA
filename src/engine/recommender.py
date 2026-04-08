"""Core recommendation engine: FAISS search + filtering with pipeline tracking."""

from __future__ import annotations

import json
import time
from dataclasses import dataclass, field
from pathlib import Path

import numpy as np

from src.data.schemas import Course, PipelineStep, Student
from src.engine.embedder import Embedder
from src.engine.indexer import load_index


@dataclass
class PipelineStats:
    """Tracks metrics from the last recommendation call."""
    total_courses: int = 0
    eligible_after_filter: int = 0
    candidates_after_search: int = 0
    steps: list[PipelineStep] = field(default_factory=list)


class Recommender:
    """Recommend courses to students using FAISS similarity search."""

    def __init__(
        self,
        index_path: str | Path = "data/processed/faiss.index",
        courses_path: str | Path = "data/raw/courses.json",
        model_name: str = "all-MiniLM-L6-v2",
    ) -> None:
        self.index = load_index(index_path)
        raw = json.loads(Path(courses_path).read_text(encoding="utf-8"))
        self.courses = [Course(**c) for c in raw]
        self.courses_by_id = {c.id: c for c in self.courses}
        self.embedder = Embedder(model_name)
        self.last_stats = PipelineStats()

    def recommend(
        self, student: Student, top_k: int = 5
    ) -> list[tuple[Course, float]]:
        """Return top-k recommended courses with pipeline step tracking."""
        steps: list[PipelineStep] = []
        self.last_stats = PipelineStats(total_courses=len(self.courses))

        # Step 1: Hard filtering
        t0 = time.perf_counter()
        completed = set(student.completed_courses)
        eligible_ids: set[str] = set()
        for course in self.courses:
            if course.id in completed:
                continue
            # Check prerequisites are met
            if course.prerequisites and not all(p in completed for p in course.prerequisites):
                continue
            eligible_ids.add(course.id)

        t1 = time.perf_counter()
        self.last_stats.eligible_after_filter = len(eligible_ids)
        steps.append(PipelineStep(
            name="hard_filter",
            duration_ms=round((t1 - t0) * 1000, 2),
            detail=f"{len(eligible_ids)}/{len(self.courses)} courses eligible "
                   f"(excluded {len(completed)} completed, "
                   f"{len(self.courses) - len(eligible_ids) - len(completed)} missing prereqs)",
        ))

        # Step 2: Vector scoring
        t2 = time.perf_counter()
        query_vec = self.embedder.embed_query(student)
        t_embed = time.perf_counter()

        search_k = min(top_k * 4, self.index.ntotal)
        scores, indices = self.index.search(query_vec, k=search_k)
        t_search = time.perf_counter()

        candidates: list[tuple[Course, float]] = []
        for score, idx in zip(scores[0], indices[0]):
            course = self.courses[int(idx)]
            if course.id in eligible_ids:
                candidates.append((course, float(score)))
            if len(candidates) >= top_k:
                break

        self.last_stats.candidates_after_search = len(candidates)
        steps.append(PipelineStep(
            name="embed_query",
            duration_ms=round((t_embed - t2) * 1000, 2),
            detail=f"Encoded student profile to 384-dim vector",
        ))
        steps.append(PipelineStep(
            name="faiss_search",
            duration_ms=round((t_search - t_embed) * 1000, 2),
            detail=f"Searched {self.index.ntotal} vectors, found {len(candidates)} matches",
        ))

        self.last_stats.steps = steps
        return candidates
