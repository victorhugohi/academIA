"""FastAPI route definitions for academIA."""

from __future__ import annotations

import time

from fastapi import APIRouter, HTTPException

from src.data.schemas import (
    Course,
    PipelineStep,
    RecommendedCourse,
    RecommendRequest,
    RecommendResponse,
    Student,
)
from src.engine.embedder import student_to_query
from src.engine.recommender import Recommender
from src.llm.client import LLMClient

router = APIRouter(prefix="/api")

# These are set by main.py on startup
recommender: Recommender | None = None
llm_client: LLMClient | None = None
_courses: list[Course] = []
_students: list[Student] = []


def init(rec: Recommender, llm: LLMClient | None, courses: list[Course], students: list[Student]) -> None:
    """Initialize shared state from the app startup."""
    global recommender, llm_client, _courses, _students
    recommender = rec
    llm_client = llm
    _courses = courses
    _students = students


def _find_student(student_id: str) -> Student:
    for s in _students:
        if s.id == student_id:
            return s
    raise HTTPException(status_code=404, detail=f"Student '{student_id}' not found")


@router.get("/health")
def health():
    ollama_up = llm_client.is_available() if llm_client else False
    return {
        "status": "ok",
        "ollama": ollama_up,
        "model": llm_client.model if llm_client else "none",
        "index_loaded": recommender is not None and recommender.index.ntotal > 0,
        "courses_count": len(_courses),
        "students_count": len(_students),
    }


@router.get("/courses", response_model=list[Course])
def list_courses():
    return _courses


@router.get("/courses/{course_id}", response_model=Course)
def get_course(course_id: str):
    for c in _courses:
        if c.id == course_id:
            return c
    raise HTTPException(status_code=404, detail=f"Course '{course_id}' not found")


@router.get("/students", response_model=list[Student])
def list_students():
    return sorted(_students, key=lambda s: s.name)


@router.get("/students/{student_id}", response_model=Student)
def get_student(student_id: str):
    return _find_student(student_id)


@router.post("/recommend", response_model=RecommendResponse)
def recommend(req: RecommendRequest):
    if not 1 <= req.top_k <= 10:
        raise HTTPException(status_code=422, detail="top_k must be between 1 and 10")

    student = _find_student(req.student_id)
    start = time.perf_counter()
    pipeline: list[PipelineStep] = []

    query_text = student_to_query(student)

    # Recommendation engine (includes filter, embed, search steps)
    results = recommender.recommend(student, top_k=req.top_k)
    pipeline.extend(recommender.last_stats.steps)

    # LLM explanations
    explanations: dict[str, str] = {}
    ollama_available = False
    if req.use_llm and llm_client:
        t_llm = time.perf_counter()
        explanations, llm_ms, ollama_available = llm_client.explain_recommendations(
            student, results
        )
        pipeline.append(PipelineStep(
            name="llm_explain",
            duration_ms=round(llm_ms, 2),
            detail=f"{'Ollama' if ollama_available else 'Fallback'}: "
                   f"generated {len(explanations)} explanations",
        ))
    elif not req.use_llm:
        pipeline.append(PipelineStep(
            name="llm_explain",
            duration_ms=0,
            detail="Skipped (use_llm=false)",
        ))

    recommendations = [
        RecommendedCourse(
            course=course,
            similarity_score=round(score, 4),
            explanation=explanations.get(course.id),
        )
        for course, score in results
    ]

    elapsed = time.perf_counter() - start

    return RecommendResponse(
        student=student,
        recommendations=recommendations,
        query_text=query_text,
        elapsed_seconds=round(elapsed, 3),
        pipeline=pipeline,
        ollama_available=ollama_available,
    )
