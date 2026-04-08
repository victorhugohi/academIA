"""Ollama LLM client with availability checking and graceful fallback."""

from __future__ import annotations

import json
import logging
import os
import time

import httpx
from ollama import Client

from src.data.schemas import Course, Student
from src.llm.prompts import build_recommendation_prompt

log = logging.getLogger(__name__)

DEFAULT_HOST = os.getenv("OLLAMA_HOST", "http://localhost:11434")
DEFAULT_MODEL = os.getenv("OLLAMA_MODEL", "qwen2.5:1.5b")
TIMEOUT_SECONDS = 30


class LLMClient:
    """Wraps Ollama to generate personalized course explanations."""

    def __init__(
        self,
        host: str = DEFAULT_HOST,
        model: str = DEFAULT_MODEL,
    ) -> None:
        self.client = Client(host=host)
        self.host = host
        self.model = model

    def is_available(self) -> bool:
        """Ping Ollama health endpoint."""
        try:
            resp = httpx.get(f"{self.host}/api/tags", timeout=3)
            return resp.status_code == 200
        except Exception:
            return False

    def explain_recommendations(
        self,
        student: Student,
        recommendations: list[tuple[Course, float]],
    ) -> tuple[dict[str, str], float, bool]:
        """Generate explanations. Returns (explanations, duration_ms, ollama_was_used).

        Falls back to template explanations if Ollama is unavailable.
        """
        courses_data = [
            {
                "id": course.id,
                "title": course.title,
                "description": course.description,
                "score": score,
            }
            for course, score in recommendations
        ]

        if not self.is_available():
            log.warning("Ollama unavailable, using fallback explanations")
            return self._fallback(student, recommendations), 0.0, False

        prompt = build_recommendation_prompt(
            student_name=student.name,
            major=student.major,
            year=student.year,
            interests=student.interests,
            courses=courses_data,
        )

        t0 = time.perf_counter()
        try:
            response = self.client.chat(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                options={"temperature": 0.7, "num_predict": 512},
            )
            duration_ms = (time.perf_counter() - t0) * 1000
            log.info(f"Ollama response in {duration_ms:.0f}ms")

            explanations = self._parse_explanations(response.message.content)
            if not explanations:
                # Parsing failed — use full response for first, fallback for rest
                full_text = response.message.content.strip()
                explanations = {}
                for i, (course, _) in enumerate(recommendations):
                    if i == 0:
                        explanations[course.id] = full_text
                    else:
                        explanations[course.id] = "See main explanation above."
            return explanations, duration_ms, True

        except Exception as e:
            duration_ms = (time.perf_counter() - t0) * 1000
            log.error(f"Ollama error after {duration_ms:.0f}ms: {e}")
            return self._fallback(student, recommendations), duration_ms, False

    @staticmethod
    def _fallback(
        student: Student, recommendations: list[tuple[Course, float]]
    ) -> dict[str, str]:
        """Generate template explanations without LLM."""
        interests = ", ".join(student.interests[:2])
        return {
            course.id: (
                f"{course.title} is recommended based on your interest in "
                f"{interests} and your current academic level (year {student.year})."
            )
            for course, _ in recommendations
        }

    @staticmethod
    def _parse_explanations(text: str) -> dict[str, str]:
        """Parse the LLM JSON response into a course_id -> explanation dict."""
        text = text.strip()
        start = text.find("[")
        end = text.rfind("]") + 1
        if start == -1 or end == 0:
            return {}
        try:
            items = json.loads(text[start:end])
            return {item["course_id"]: item["explanation"] for item in items}
        except (json.JSONDecodeError, KeyError):
            return {}
