"""FastAPI application for academIA."""

from __future__ import annotations

import json
import logging
import time
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse

from src.api.routes import init, router
from src.data.schemas import Course, Student
from src.engine.recommender import Recommender
from src.llm.client import LLMClient

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s │ %(levelname)-7s │ %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger("academIA")

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
DATA_DIR = PROJECT_ROOT / "data"


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Load data and models on startup."""
    t0 = time.perf_counter()

    courses_raw = json.loads((DATA_DIR / "raw/courses.json").read_text(encoding="utf-8"))
    students_raw = json.loads((DATA_DIR / "raw/students.json").read_text(encoding="utf-8"))
    courses = [Course(**c) for c in courses_raw]
    students = [Student(**s) for s in students_raw]
    log.info(f"Loaded {len(courses)} courses, {len(students)} students")

    recommender = Recommender(
        index_path=DATA_DIR / "processed/faiss.index",
        courses_path=DATA_DIR / "raw/courses.json",
    )
    log.info(f"FAISS index: {recommender.index.ntotal} vectors")

    llm = LLMClient()
    ollama_up = llm.is_available()
    log.info(f"Ollama: {'online' if ollama_up else 'offline'} ({llm.model})")

    init(recommender, llm, courses, students)

    elapsed = (time.perf_counter() - t0) * 1000
    log.info(f"Startup complete in {elapsed:.0f}ms")
    yield


app = FastAPI(
    title="academIA",
    version="1.0.0",
    description="Course Recommendation System — FLISoL Demo",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log each request with method, path, status, and duration."""
    start = time.perf_counter()
    response = await call_next(request)
    duration_ms = (time.perf_counter() - start) * 1000
    log.info(f"{request.method} {request.url.path} → {response.status_code} ({duration_ms:.0f}ms)")
    return response


app.include_router(router)


@app.get("/")
def serve_demo():
    """Serve the web demo at root."""
    demo_path = PROJECT_ROOT / "demo/index.html"
    if demo_path.exists():
        return FileResponse(demo_path, media_type="text/html")
    return {"message": "academIA API is running. Visit /docs for the API explorer."}
