from typing import Literal, Optional

from pydantic import BaseModel


class Course(BaseModel):
    id: str
    title: str
    department: str
    description: str
    tags: list[str]
    difficulty: Literal["introductory", "intermediate", "advanced"]
    credits: int
    prerequisites: list[str] = []


class Student(BaseModel):
    id: str
    name: str
    major: str
    year: int
    interests: list[str]
    completed_courses: list[str] = []


class Enrollment(BaseModel):
    student_id: str
    course_id: str
    semester: str
    grade: Optional[float] = None


class RecommendRequest(BaseModel):
    student_id: str
    top_k: int = 5
    use_llm: bool = True


class RecommendedCourse(BaseModel):
    course: Course
    similarity_score: float
    explanation: Optional[str] = None


class PipelineStep(BaseModel):
    name: str
    duration_ms: float
    detail: str = ""


class RecommendResponse(BaseModel):
    student: Student
    recommendations: list[RecommendedCourse]
    query_text: str
    elapsed_seconds: float
    pipeline: list[PipelineStep] = []
    ollama_available: bool = False
