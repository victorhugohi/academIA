"""Embedding utilities for courses and student queries."""

from __future__ import annotations

import numpy as np
from sentence_transformers import SentenceTransformer

from src.data.schemas import Course, Student

DEFAULT_MODEL = "all-MiniLM-L6-v2"


def course_to_text(course: Course) -> str:
    """Build a single text representation of a course for embedding."""
    tags = ", ".join(course.tags)
    return (
        f"{course.title}. {course.description} "
        f"Topics: {tags}. "
        f"Department: {course.department}. "
        f"Level: {course.difficulty}."
    )


def student_to_query(student: Student) -> str:
    """Build a query string from a student profile."""
    interests = ", ".join(student.interests)
    return f"A {student.major} student interested in {interests}."


class Embedder:
    """Wrapper around SentenceTransformer for course/student embeddings."""

    def __init__(self, model_name: str = DEFAULT_MODEL) -> None:
        self.model = SentenceTransformer(model_name)

    def embed_courses(self, courses: list[Course]) -> np.ndarray:
        """Embed a list of courses, returning normalized vectors."""
        texts = [course_to_text(c) for c in courses]
        return self.model.encode(texts, normalize_embeddings=True)

    def embed_query(self, student: Student) -> np.ndarray:
        """Embed a student profile as a query vector."""
        text = student_to_query(student)
        return self.model.encode([text], normalize_embeddings=True).astype("float32")
