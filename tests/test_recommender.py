"""Tests for the recommendation engine."""

import pytest

from src.data.schemas import Student
from src.engine.recommender import Recommender


@pytest.fixture(scope="module")
def recommender():
    return Recommender()


def test_cs_student_gets_cs_courses(recommender):
    """A CS student interested in AI should get ML-related courses."""
    student = Student(
        id="T1", name="Test", major="Computer Science", year=3,
        interests=["artificial intelligence", "machine learning"],
        completed_courses=[],
    )
    results = recommender.recommend(student, top_k=5)
    course_ids = [c.id for c, _ in results]
    assert any(cid.startswith("CS") for cid in course_ids)


def test_completed_courses_excluded(recommender):
    """Courses already taken should not appear in recommendations."""
    student = Student(
        id="T2", name="Test", major="Computer Science", year=2,
        interests=["programming", "algorithms"],
        completed_courses=["CS101", "CS201"],
    )
    results = recommender.recommend(student, top_k=5)
    course_ids = [c.id for c, _ in results]
    assert "CS101" not in course_ids
    assert "CS201" not in course_ids


def test_cross_domain_recommendations(recommender):
    """Cross-domain interests should produce diverse department results."""
    student = Student(
        id="T3", name="Test", major="Arts", year=2,
        interests=["digital art", "programming", "creative coding"],
        completed_courses=[],
    )
    results = recommender.recommend(student, top_k=5)
    departments = {c.department for c, _ in results}
    assert len(departments) >= 2


def test_recommendation_count(recommender):
    """Should return exactly top_k results."""
    student = Student(
        id="T4", name="Test", major="Mathematics", year=1,
        interests=["calculus"], completed_courses=[],
    )
    results = recommender.recommend(student, top_k=3)
    assert len(results) == 3


def test_scores_are_sorted(recommender):
    """Results should be sorted by descending similarity score."""
    student = Student(
        id="T5", name="Test", major="Physics", year=2,
        interests=["quantum mechanics", "simulation"],
        completed_courses=[],
    )
    results = recommender.recommend(student, top_k=5)
    scores = [s for _, s in results]
    assert scores == sorted(scores, reverse=True)
