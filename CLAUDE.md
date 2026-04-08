# academIA - Course Recommendation System

## Project Overview
Demo project for FLISoL talk. Recommends university courses to students
using FAISS vector similarity + Ollama LLM explanations.

## Tech Stack
- Python 3.11+, FastAPI, Pydantic v2
- sentence-transformers (all-MiniLM-L6-v2)
- faiss-cpu
- ollama (Python client)

## Key Commands
- `pip install -r requirements.txt` - Install dependencies
- `python src/data/generator.py` - Generate synthetic data
- `python scripts/build_index.py` - Build FAISS index
- `bash scripts/setup_parrot.sh` - Pull Ollama model
- `uvicorn src.api.main:app --reload` - Run API server
- `python demo/cli.py` - Run CLI demo
- `pytest tests/` - Run tests

## Architecture
1. Synthetic data (JSON) -> Embeddings (numpy) -> FAISS index
2. Query: student profile -> embed -> FAISS search -> top-k courses
3. LLM: Ollama explains why each course fits the student

## Conventions
- All code in English
- Type hints on all function signatures
- Pydantic models for all data structures
- Keep functions small and single-purpose
