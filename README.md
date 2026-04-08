# academIA

Course recommendation system demo for FLISoL. Recommends university courses to students using **FAISS vector similarity search** + **Ollama LLM explanations**.

## Architecture

```
Student Profile → Embed (MiniLM) → FAISS Search → Top-K Courses → Ollama → Personalized Explanations
```

- **50 courses** across 6 departments (CS, Math, Physics, Arts, Literature, Business)
- **20 students** with diverse profiles and interests
- Embeddings: `all-MiniLM-L6-v2` (384-dim, ~80MB)
- Vector index: FAISS `IndexFlatIP` (cosine similarity)
- LLM: Ollama with `qwen2.5:1.5b` (runs on any laptop)

## Quick Start

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Generate synthetic data
python -m src.data.generator

# 3. Build embeddings + FAISS index
python -m scripts.build_index

# 4. (Optional) Set up Ollama for LLM explanations
bash scripts/setup_parrot.sh

# 5a. Run the CLI demo
python demo/cli.py

# 5b. Or run the web demo
uvicorn src.api.main:app --reload
# Open http://localhost:8000
```

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/health` | Health check |
| GET | `/api/courses` | List all courses |
| GET | `/api/courses/{id}` | Get single course |
| GET | `/api/students` | List all students |
| GET | `/api/students/{id}` | Get single student |
| POST | `/api/recommend` | Get recommendations |

### POST /api/recommend

```json
{
  "student_id": "STU001",
  "top_k": 5,
  "use_llm": true
}
```

## Tests

```bash
pytest tests/
```

## Project Structure

```
├── src/
│   ├── data/       # Pydantic schemas + data generator
│   ├── engine/     # Embedder, FAISS indexer, recommender
│   ├── llm/        # Ollama client + prompt templates
│   └── api/        # FastAPI app + routes
├── demo/
│   ├── cli.py      # Interactive CLI demo
│   └── index.html  # Single-page web demo
├── scripts/
│   ├── build_index.py    # Build FAISS index
│   └── setup_parrot.sh   # Pull Ollama model
└── tests/
```

## Tech Stack

Python 3.11+ | FastAPI | sentence-transformers | FAISS | Ollama | Pydantic v2
