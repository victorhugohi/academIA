"""Tests for the FastAPI endpoints."""

import pytest
from fastapi.testclient import TestClient

from src.api.main import app


@pytest.fixture(scope="module")
def client():
    with TestClient(app) as c:
        yield c


def test_health(client):
    res = client.get("/api/health")
    assert res.status_code == 200
    assert res.json()["status"] == "ok"


def test_list_courses(client):
    res = client.get("/api/courses")
    assert res.status_code == 200
    courses = res.json()
    assert len(courses) == 50


def test_get_course(client):
    res = client.get("/api/courses/CS101")
    assert res.status_code == 200
    assert res.json()["title"] == "Introduction to Programming"


def test_get_course_not_found(client):
    res = client.get("/api/courses/FAKE999")
    assert res.status_code == 404


def test_list_students(client):
    res = client.get("/api/students")
    assert res.status_code == 200
    students = res.json()
    assert len(students) == 20


def test_get_student(client):
    res = client.get("/api/students/STU001")
    assert res.status_code == 200
    assert res.json()["name"] == "Alice Chen"


def test_get_student_not_found(client):
    res = client.get("/api/students/FAKE999")
    assert res.status_code == 404


def test_recommend_no_llm(client):
    res = client.post("/api/recommend", json={
        "student_id": "STU001",
        "top_k": 3,
        "use_llm": False,
    })
    assert res.status_code == 200
    data = res.json()
    assert len(data["recommendations"]) == 3
    assert data["elapsed_seconds"] > 0
    assert data["query_text"] != ""


def test_recommend_invalid_student(client):
    res = client.post("/api/recommend", json={
        "student_id": "INVALID",
        "top_k": 3,
        "use_llm": False,
    })
    assert res.status_code == 404
