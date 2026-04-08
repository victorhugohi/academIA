
<div align="center">

```
╔═══════════════════════════════════╗
║         AcademIA v1.0             ║
║   Course Recommendation Engine    ║
║    Powered by open-source AI      ║
╚═══════════════════════════════════╝
```

**A course recommendation system that combines vector similarity search with LLM-powered explanations.**

Built for [FLISoL](https://flisol.info/) — Festival Latinoamericano de Instalacion de Software Libre.

[![Python 3.11+](https://img.shields.io/badge/python-3.11%2B-blue)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-green)](https://fastapi.tiangolo.com)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![FAISS](https://img.shields.io/badge/FAISS-vector%20search-orange)](https://github.com/facebookresearch/faiss)
[![Ollama](https://img.shields.io/badge/Ollama-local%20LLM-purple)](https://ollama.com)

---

[How It Works](#how-it-works) · [Quick Start](#quick-start) · [Windows Setup](#windows-setup) · [Parrot OS Setup](#parrot-os-usb-setup) · [API Reference](#api-reference) · [Architecture](#architecture)

</div>

---

## How It Works

AcademIA recommends university courses to students using a two-stage hybrid AI pipeline:

```
┌─────────────┐     ┌──────────────┐     ┌─────────────┐     ┌──────────────┐
│   Student    │────>│   Embed      │────>│   FAISS     │────>│   Ollama     │
│   Profile    │     │  (MiniLM)    │     │   Search    │     │   Explain    │
└─────────────┘     └──────────────┘     └─────────────┘     └──────────────┘
  interests          384-dim vector       top-K courses       personalized
  major, year        in ~5ms              in <1ms             explanations
```

**Stage 1 — Vector Search (instant):** The student's profile (interests, major) is encoded into a 384-dimensional vector using [sentence-transformers](https://www.sbert.net/). This vector is compared against pre-computed course embeddings using [FAISS](https://github.com/facebookresearch/faiss) inner product search. Results in under 1ms.

**Stage 2 — LLM Explanation (optional):** The top courses are sent to a local [Ollama](https://ollama.com) model that generates personalized explanations for why each course fits the student. If Ollama is offline, the system falls back to template-based explanations — the demo never breaks.

### The Pipeline Monitor

Every recommendation request returns detailed step-by-step timing:

```
│ FILTER          <1ms   45/50 courses eligible (excluded 6 completed, 0 missing prereqs)
│ EMBED            5ms   Encoded student profile to 384-dim vector
│ SEARCH          <1ms   Searched 50 vectors, found 5 matches
│ LLM           3200ms   Ollama: generated 5 explanations
│
└─ TOTAL: 3207ms
```

This makes every step of the AI pipeline visible and measurable — perfect for understanding what's happening under the hood.

---

## What's Inside

- **50 courses** across 6 departments (CS, Math, Physics, Arts, Literature, Business)
- **20 students** with diverse profiles — obvious matches, cross-domain interests, niche specializations
- **~100 enrollments** linking students to completed courses
- **Prerequisite filtering** — only recommends courses whose prerequisites the student has completed
- **Graceful degradation** — works fully offline without Ollama, just without LLM explanations

---

## Quick Start

If you just want to get it running fast:

```bash
git clone https://github.com/victorhugohi/academIA.git
cd academIA
pip install -r requirements.txt
python -m src.data.generator
python -m scripts.build_index
python -m uvicorn src.api.main:app --reload
```

Open http://localhost:8000 — done.

For complete step-by-step instructions, see [Windows Setup](#windows-setup) or [Parrot OS Setup](#parrot-os-usb-setup) below.

---

## Windows Setup

Complete guide to running academIA on Windows 10/11.

### Prerequisites

| Requirement | Version | Check |
|---|---|---|
| Python | 3.11 or higher | `python --version` |
| pip | any recent version | `pip --version` |
| Git | any recent version | `git --version` |

> Python 3.11+ is required because the project uses modern type hints (`list[str]`, `X | None`). Download from [python.org](https://www.python.org/downloads/) if needed — make sure to check "Add to PATH" during installation.

### Step 1 — Clone the Repository

Open a terminal (PowerShell, Command Prompt, or Git Bash):

```bash
git clone https://github.com/victorhugohi/academIA.git
cd academIA
```

### Step 2 — Create a Virtual Environment (recommended)

```bash
python -m venv .venv
```

Activate it:

```bash
# PowerShell
.venv\Scripts\Activate.ps1

# Command Prompt
.venv\Scripts\activate.bat

# Git Bash
source .venv/Scripts/activate
```

You should see `(.venv)` in your prompt.

### Step 3 — Install Dependencies

```bash
pip install -r requirements.txt
```

This installs: FastAPI, sentence-transformers (downloads ~80MB model on first run), FAISS, Ollama client, and other dependencies. Total download is approximately 500MB due to PyTorch.

### Step 4 — Generate Synthetic Data

```bash
python -m src.data.generator
```

Expected output:
```
Generated 50 courses, 20 students, 97 enrollments in data\raw/
```

This creates three JSON files in `data/raw/`:
- `courses.json` — 50 university courses with descriptions, tags, and prerequisites
- `students.json` — 20 students with interests, majors, and completed courses
- `enrollments.json` — enrollment records linking students to courses

### Step 5 — Build the FAISS Index

```bash
python -m scripts.build_index
```

Expected output:
```
Embedding 50 courses...
Saved embeddings to data\processed\embeddings.npy (shape: (50, 384))
Saved FAISS index to data\processed\faiss.index (50 vectors)
```

This step:
1. Loads the `all-MiniLM-L6-v2` model (~80MB, downloaded and cached automatically)
2. Converts each course into a 384-dimensional vector
3. Builds a FAISS inner product index for fast similarity search
4. Saves both the raw embeddings and the FAISS index to `data/processed/`

### Step 6 — (Optional) Set Up Ollama for LLM Explanations

Ollama is optional. Without it, the system still works — you get similarity-based recommendations without natural language explanations.

1. Download and install Ollama from https://ollama.com/download
2. Open a **separate terminal** and start the server:
   ```bash
   ollama serve
   ```
3. Pull the model (in another terminal):
   ```bash
   ollama pull qwen2.5:1.5b
   ```
4. Verify it works:
   ```bash
   ollama run qwen2.5:1.5b "Say hello in one sentence."
   ```

The `qwen2.5:1.5b` model is ~1GB and runs on any machine with 2GB+ RAM. No GPU required.

### Step 7 — Run the Application

You have two options:

**Option A — Web UI (recommended for demos):**

```bash
python -m uvicorn src.api.main:app --reload
```

Open http://localhost:8000 in your browser. You'll see the terminal-themed web interface.

The server logs every request with timing:
```
12:30:01 │ INFO    │ academIA loaded: 50 courses, 20 students
12:30:01 │ INFO    │ FAISS index: 50 vectors
12:30:01 │ INFO    │ Ollama: online (qwen2.5:1.5b)
12:30:01 │ INFO    │ Startup complete in 1823ms
12:30:05 │ INFO    │ GET /api/health → 200 (45ms)
12:30:12 │ INFO    │ POST /api/recommend → 200 (3241ms)
```

**Option B — CLI demo (works without a server):**

```bash
python demo/cli.py
```

Interactive terminal demo with colored output, pipeline timing, and student selection.

### Step 8 — Run Tests

```bash
python -m pytest tests/ -v
```

Expected: 14 tests pass (9 API tests + 5 recommender tests).

### Troubleshooting (Windows)

| Problem | Solution |
|---|---|
| `python` not found | Use `python3` or `py` instead. Or reinstall Python with "Add to PATH" checked. |
| `pip install` fails with permissions | Use `python -m pip install -r requirements.txt` |
| Port 8000 already in use | Use `python -m uvicorn src.api.main:app --reload --port 8001` |
| `ModuleNotFoundError: No module named 'src'` | Make sure you're running from the project root (`academIA/` directory) |
| FAISS index not found | Run `python -m scripts.build_index` first |
| Ollama connection refused | Make sure `ollama serve` is running in a separate terminal |
| Slow first run | Normal — the embedding model (~80MB) downloads on first use and is cached after |

---

## Parrot OS USB Setup

Complete guide to running academIA on a bootable Parrot OS Security Edition USB drive. This setup lets you carry the full demo environment in your pocket.

### What You Need

- A **128GB+ USB drive** (USB 3.0 or USB-C recommended for speed)
- A computer with internet access for the initial setup
- Approximately 30-40 minutes for the full process

### Phase 1 — Create the Parrot OS USB

#### Step 1.1 — Download Parrot OS

Download **Parrot OS Security Edition** ISO from:
https://parrotlinux.org/download/

Choose the **Security Edition** (includes all tools). The ISO is approximately 4-5GB.

Verify the checksum after download:
```bash
# The checksum is listed on the download page
sha256sum Parrot-security-*.iso
```

#### Step 1.2 — Flash the ISO to USB

**From Windows**, use [Rufus](https://rufus.ie/):

1. Download and open Rufus
2. Insert your 128GB USB drive
3. Select the Parrot OS ISO
4. Partition scheme: **GPT**
5. Target system: **UEFI**
6. File system: **FAT32** (Rufus may suggest this automatically)
7. Click **START**
8. When prompted, select **Write in DD Image mode** (important for Parrot OS)
9. Wait for the write to complete (~5-10 minutes)

**From Linux**, use `dd`:
```bash
# Find your USB device (be VERY careful to select the right one)
lsblk

# Flash the ISO (replace /dev/sdX with your USB device)
sudo dd if=Parrot-security-*.iso of=/dev/sdX bs=4M status=progress
sync
```

#### Step 1.3 — Boot from USB

1. Restart your computer
2. Enter the boot menu (usually **F12**, **F2**, or **ESC** during startup — varies by manufacturer)
3. Select your USB drive from the boot menu
4. Choose **Try / Install** from the Parrot boot menu

#### Step 1.4 — Install Parrot OS to the USB (Full Install)

> **Why a full install instead of live mode?** A full install gives you persistent storage, proper NVIDIA driver support, and behaves like a normal OS. Live mode with persistence works but can be flaky with kernel modules.

Once booted into the live session:

1. Open the **Install Parrot** application from the desktop
2. Follow the Calamares installer:
   - Language, timezone, keyboard — choose your preferences
   - **Partitioning**: Select **"Erase disk"** and make sure you select **your USB drive** (not the computer's internal disk!)
   - Verify the target disk size matches your USB (128GB)
   - Create a user account and password
3. Click **Install** and wait (~15-20 minutes)
4. When complete, click **Restart Now**
5. Remove any other USB drives so it boots from the Parrot USB

After reboot, you'll have a full Parrot OS installation on your USB drive.

### Phase 2 — System Setup

Boot into your new Parrot OS installation and open a terminal.

#### Step 2.1 — Update the System

```bash
sudo apt-get update && sudo apt-get upgrade -y
```

#### Step 2.2 — NVIDIA Drivers (if your demo machine has an NVIDIA GPU)

Check if a GPU is detected:
```bash
lspci | grep -i nvidia
```

If you see a GPU listed:
```bash
sudo apt-get install -y nvidia-driver firmware-misc-nonfree
```

After installation, **reboot**:
```bash
sudo reboot
```

After rebooting, verify:
```bash
nvidia-smi
```

You should see your GPU name and VRAM. If `nvidia-smi` is not found, the driver needs a reboot or a different driver version.

> **Note:** If the demo machine doesn't have an NVIDIA GPU, skip this step entirely. AcademIA runs fine on CPU — Ollama and sentence-transformers both support CPU inference.

#### Step 2.3 — Install Python 3.11+

Parrot OS usually includes Python 3.11+. Verify:

```bash
python3 --version
```

If the version is below 3.11:
```bash
sudo apt-get install -y python3.11 python3.11-venv python3.11-dev
```

### Phase 3 — AcademIA Setup

#### Step 3.1 — Clone the Repository

```bash
cd ~
git clone https://github.com/victorhugohi/academIA.git
cd academIA
```

#### Step 3.2 — Create a Virtual Environment

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Your prompt should now show `(.venv)`.

#### Step 3.3 — Install Python Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

This downloads ~500MB (PyTorch, sentence-transformers, etc.). On a good connection, takes 2-5 minutes.

Verify all key packages are importable:
```bash
python -c "import fastapi, faiss, sentence_transformers, ollama; print('All packages OK')"
```

#### Step 3.4 — Generate Data and Build Index

```bash
python -m src.data.generator
python -m scripts.build_index
```

Expected output:
```
Generated 50 courses, 20 students, 97 enrollments in data/raw/
Embedding 50 courses...
Saved embeddings to data/processed/embeddings.npy (shape: (50, 384))
Saved FAISS index to data/processed/faiss.index (50 vectors)
```

#### Step 3.5 — Install and Configure Ollama

```bash
curl -fsSL https://ollama.com/install.sh | sh
```

Start the Ollama server:
```bash
ollama serve &
```

Wait a few seconds, then pull the model:
```bash
ollama pull qwen2.5:1.5b
```

Verify:
```bash
ollama run qwen2.5:1.5b "Say hello in one sentence."
```

#### Step 3.6 — Run the Full Setup Script (Alternative to Steps 3.2-3.5)

Instead of running steps 3.2 through 3.5 manually, you can use the automated setup script that does everything at once:

```bash
cd ~/academIA
bash scripts/setup_parrot.sh
```

This script:
1. Detects your OS and hardware (RAM, disk, GPU)
2. Checks for NVIDIA drivers
3. Creates a Python virtual environment
4. Installs all dependencies
5. Installs Ollama and pulls the model
6. Generates data and builds the FAISS index
7. Runs a 13-point verification checklist

At the end, you'll see a checklist:
```
══ 8. Final Verification ══
  [✓] NVIDIA driver installed
  [✓] Python 3.11.x
  [✓] FastAPI importable
  [✓] FAISS importable
  [✓] sentence-transformers importable
  [✓] Ollama Python client importable
  [✓] Ollama server responding
  [✓] qwen2.5:1.5b available
  [✓] courses.json exists
  [✓] students.json exists
  [✓] faiss.index exists
  [✓] FastAPI app imports
  [✓] Recommender imports

  Results: 13/13 checks passed

╔═══════════════════════════════════════════════╗
║  AcademIA is ready!                           ║
║  CLI:  python demo/cli.py                     ║
║  Web:  uvicorn src.api.main:app --reload      ║
╚═══════════════════════════════════════════════╝
```

### Phase 4 — Run the Demo

Make sure you're in the project directory with the virtual environment activated:

```bash
cd ~/academIA
source .venv/bin/activate
```

**Web UI:**
```bash
python -m uvicorn src.api.main:app --reload
```

Open Firefox and go to http://localhost:8000

**CLI demo:**
```bash
python demo/cli.py
```

**Run tests to verify everything works:**
```bash
python -m pytest tests/ -v
```

### Pre-Presentation Checklist

Run through this before your FLISoL talk:

```
[ ] USB boots successfully on the presentation machine
[ ] NVIDIA drivers load (nvidia-smi shows GPU) — or confirm CPU mode works
[ ] Virtual environment activates: source .venv/bin/activate
[ ] Ollama is running: curl http://localhost:11434/api/tags
[ ] Web UI loads at http://localhost:8000
[ ] Select a student and get recommendations (with LLM)
[ ] Pipeline monitor shows all 4 steps with timing
[ ] CLI demo works: python demo/cli.py
[ ] Projector/screen resolution looks OK with the terminal theme
```

### Troubleshooting (Parrot OS)

| Problem | Solution |
|---|---|
| USB won't boot | Enter BIOS, disable Secure Boot, set USB as first boot device |
| Black screen after boot | Try `nomodeset` kernel parameter: edit GRUB entry, add `nomodeset` to linux line |
| `nvidia-smi` not found after install | Reboot required. If still fails: `sudo apt-get install -y nvidia-driver` |
| `python3: command not found` | `sudo apt-get install -y python3.11` |
| `pip install` SSL errors | `sudo apt-get install -y ca-certificates` then retry |
| Ollama won't start | Check if port 11434 is free: `sudo lsof -i :11434`. Kill any existing process. |
| Slow USB performance | Use a USB 3.0+ port (usually blue). USB 2.0 will work but is noticeably slower. |
| Wi-Fi not working | Parrot OS includes most drivers. Try: `sudo apt-get install -y firmware-iwlwifi` then reboot |
| No sound / display issues | Connect to projector BEFORE booting for best results |

---

## API Reference

Base URL: `http://localhost:8000`

Interactive documentation (Swagger UI) is available at http://localhost:8000/docs when the server is running.

### GET /api/health

Check system status.

**Response:**
```json
{
  "status": "ok",
  "ollama": true,
  "model": "qwen2.5:1.5b",
  "index_loaded": true,
  "courses_count": 50,
  "students_count": 20
}
```

### GET /api/students

List all students, sorted alphabetically.

**Response:** Array of Student objects.
```json
[
  {
    "id": "STU001",
    "name": "Alice Chen",
    "major": "Computer Science",
    "year": 3,
    "interests": ["machine learning", "neural networks", "data science"],
    "completed_courses": ["CS101", "CS150", "CS201", "CS210", "MATH101", "MATH201"]
  }
]
```

### GET /api/students/{student_id}

Get a single student. Returns `404` if not found.

### GET /api/courses

List all 50 courses.

**Response:** Array of Course objects.
```json
[
  {
    "id": "CS340",
    "title": "Machine Learning",
    "department": "Computer Science",
    "description": "Introduction to machine learning algorithms...",
    "tags": ["machine learning", "AI", "neural networks", "python", "data science"],
    "difficulty": "advanced",
    "credits": 4,
    "prerequisites": ["CS201", "MATH201"]
  }
]
```

### GET /api/courses/{course_id}

Get a single course. Returns `404` if not found.

### POST /api/recommend

Get personalized course recommendations for a student.

**Request:**
```json
{
  "student_id": "STU001",
  "top_k": 5,
  "use_llm": true
}
```

| Field | Type | Default | Description |
|---|---|---|---|
| `student_id` | string | required | Student ID (e.g., "STU001") |
| `top_k` | integer | 5 | Number of recommendations (1-10) |
| `use_llm` | boolean | true | Generate LLM explanations |

**Response:**
```json
{
  "student": { "id": "STU001", "name": "Alice Chen", "..." : "..." },
  "recommendations": [
    {
      "course": { "id": "CS340", "title": "Machine Learning", "..." : "..." },
      "similarity_score": 0.8912,
      "explanation": "This course directly aligns with your interest in neural networks..."
    }
  ],
  "query_text": "A Computer Science student interested in machine learning, neural networks, data science.",
  "elapsed_seconds": 3.241,
  "pipeline": [
    { "name": "hard_filter", "duration_ms": 0.12, "detail": "44/50 courses eligible..." },
    { "name": "embed_query", "duration_ms": 4.8, "detail": "Encoded student profile to 384-dim vector" },
    { "name": "faiss_search", "duration_ms": 0.3, "detail": "Searched 50 vectors, found 5 matches" },
    { "name": "llm_explain", "duration_ms": 3200.5, "detail": "Ollama: generated 5 explanations" }
  ],
  "ollama_available": true
}
```

**Error responses:**
- `404` — Student not found: `{"detail": "Student 'XXX' not found"}`
- `422` — Invalid top_k: `{"detail": "top_k must be between 1 and 10"}`

---

## Architecture

```
academIA/
├── src/
│   ├── data/
│   │   ├── schemas.py        # Pydantic models (Course, Student, API types)
│   │   └── generator.py      # Curated synthetic data (50 courses, 20 students)
│   ├── engine/
│   │   ├── embedder.py       # SentenceTransformer wrapper (all-MiniLM-L6-v2)
│   │   ├── indexer.py        # FAISS index build/load/save
│   │   └── recommender.py    # Recommendation pipeline with step tracking
│   ├── llm/
│   │   ├── prompts.py        # LLM prompt templates
│   │   └── client.py         # Ollama client with health check + fallback
│   └── api/
│       ├── main.py           # FastAPI app, lifespan, logging middleware
│       └── routes.py         # API endpoints (/health, /students, /courses, /recommend)
├── demo/
│   ├── cli.py                # Interactive CLI demo (rich terminal output)
│   └── index.html            # Single-file web UI (vanilla JS, terminal aesthetic)
├── scripts/
│   ├── build_index.py        # Build embeddings + FAISS index
│   └── setup_parrot.sh       # Automated Parrot OS/Debian setup
├── tests/
│   ├── test_recommender.py   # 5 tests: filtering, sorting, cross-domain, counts
│   └── test_api.py           # 9 tests: health, CRUD, recommend, error handling
├── data/
│   ├── raw/                  # Generated JSON (courses, students, enrollments)
│   └── processed/            # Embeddings (.npy) + FAISS index
├── requirements.txt
├── .env.example
└── CLAUDE.md
```

### Data Flow

```
generator.py ──> data/raw/*.json ──> build_index.py ──> data/processed/
                                                              │
                                                              v
                     Student Profile ──> embedder.py ──> recommender.py ──> routes.py
                                                              │
                                                              v
                                                         client.py (Ollama)
                                                              │
                                                              v
                                                     RecommendResponse
                                                    (courses + pipeline + explanations)
```

### Key Design Decisions

| Decision | Why |
|---|---|
| **FAISS IndexFlatIP** | At 50 courses, exact search is instant. Inner product on normalized vectors = cosine similarity. Simple to explain. |
| **all-MiniLM-L6-v2** | 384-dim, ~80MB. Great quality-to-size ratio. Embeds in <10ms. |
| **qwen2.5:1.5b via Ollama** | 1.5B params, runs on 2GB RAM, decent instruction following. Local and free. |
| **Single HTML file** | No npm, no build step. View-source friendly. Works as `file://` and via server. |
| **Graceful LLM fallback** | Demo never breaks. Shows recommendations with or without Ollama. |
| **Pipeline step tracking** | Makes the AI pipeline transparent. Every step is timed and explained. |
| **Prerequisite filtering** | Adds realism — only recommends courses the student can actually take. |
| **Curated (not random) data** | Hand-crafted course descriptions produce meaningful embeddings. Random data = meaningless demo. |

---

## Tech Stack

| Component | Technology | Purpose |
|---|---|---|
| Embeddings | [sentence-transformers](https://www.sbert.net/) / all-MiniLM-L6-v2 | Convert text to 384-dim vectors |
| Vector Search | [FAISS](https://github.com/facebookresearch/faiss) | Fast similarity search |
| LLM | [Ollama](https://ollama.com) / qwen2.5:1.5b | Generate natural language explanations |
| API | [FastAPI](https://fastapi.tiangolo.com) | REST API with auto-generated docs |
| Data Validation | [Pydantic](https://docs.pydantic.dev) v2 | Type-safe data models |
| CLI | [Rich](https://rich.readthedocs.io) | Colored terminal output |
| Testing | [pytest](https://docs.pytest.org) | Unit and integration tests |

---

## Environment Variables

Copy `.env.example` to `.env` and modify as needed:

```bash
cp .env.example .env
```

| Variable | Default | Description |
|---|---|---|
| `OLLAMA_HOST` | `http://localhost:11434` | Ollama server URL |
| `OLLAMA_MODEL` | `qwen2.5:1.5b` | LLM model for explanations |
| `EMBEDDING_MODEL` | `all-MiniLM-L6-v2` | Sentence transformer model |
| `API_HOST` | `0.0.0.0` | FastAPI bind address |
| `API_PORT` | `8000` | FastAPI port |

---

## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/my-feature`
3. Make your changes
4. Run tests: `python -m pytest tests/ -v`
5. Commit and push
6. Open a Pull Request

---

## License

[MIT](LICENSE) — use it however you want.

---

<div align="center">

Built with open-source tools for the open-source community.

**[FLISoL](https://flisol.info/)** — Because software should be free.

</div>
