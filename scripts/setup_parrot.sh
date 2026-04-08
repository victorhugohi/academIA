#!/usr/bin/env bash
# ═══════════════════════════════════════════════════════════════
#  AcademIA Setup — Parrot OS / Debian
#  Installs and verifies the full environment. Idempotent.
# ═══════════════════════════════════════════════════════════════
set -euo pipefail

LOGFILE="$(pwd)/setup.log"
MODEL="${1:-qwen2.5:1.5b}"

# ── Colors ─────────────────────────────────────────────────────
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
DIM='\033[2m'
RESET='\033[0m'

log() { echo "[$(date '+%H:%M:%S')] $*" | tee -a "$LOGFILE"; }
section() { echo -e "\n${GREEN}══ $1 ══${RESET}"; log "== $1 =="; }
ok()  { echo -e "  ${GREEN}[✓]${RESET} $1"; log "[✓] $1"; }
warn() { echo -e "  ${YELLOW}[!]${RESET} $1"; log "[!] $1"; }
fail() { echo -e "  ${RED}[✗]${RESET} $1"; log "[✗] $1"; }
die()  { fail "$1"; echo -e "\n${RED}Setup aborted. Check $LOGFILE${RESET}"; exit 1; }

echo "" > "$LOGFILE"
echo -e "${CYAN}"
cat << 'BANNER'
   ╔═══════════════════════════════════╗
   ║       AcademIA Setup v1.0        ║
   ║   Parrot OS / Debian Installer   ║
   ╚═══════════════════════════════════╝
BANNER
echo -e "${RESET}"

# ── 1. System Check ───────────────────────────────────────────
section "1. System Check"

if [ -f /etc/os-release ]; then
    . /etc/os-release
    log "OS: $PRETTY_NAME"
    echo -e "  OS:   ${CYAN}$PRETTY_NAME${RESET}"
else
    die "Cannot detect OS. /etc/os-release not found."
fi

# Accept Parrot OS, Debian, Ubuntu, and derivatives
if [[ ! "$ID_LIKE" =~ debian ]] && [[ "$ID" != "debian" ]] && [[ "$ID" != "parrot" ]] && [[ "$ID" != "ubuntu" ]]; then
    die "Unsupported OS: $ID. This script targets Debian-based systems."
fi

RAM_MB=$(free -m | awk '/Mem:/{print $2}')
DISK_AVAIL=$(df -h . | awk 'NR==2{print $4}')
echo -e "  RAM:  ${CYAN}${RAM_MB} MB${RESET}"
echo -e "  Disk: ${CYAN}${DISK_AVAIL} available${RESET}"
log "RAM: ${RAM_MB}MB, Disk: ${DISK_AVAIL}"

if command -v lspci &> /dev/null; then
    GPU=$(lspci | grep -i 'vga\|3d\|display' | head -1 || echo "None detected")
    echo -e "  GPU:  ${CYAN}${GPU}${RESET}"
    log "GPU: $GPU"
else
    echo -e "  GPU:  ${DIM}lspci not available${RESET}"
fi

ok "System check passed"

# ── 2. NVIDIA Driver ──────────────────────────────────────────
section "2. NVIDIA GPU"

if command -v nvidia-smi &> /dev/null; then
    GPU_NAME=$(nvidia-smi --query-gpu=name --format=csv,noheader 2>/dev/null | head -1)
    GPU_VRAM=$(nvidia-smi --query-gpu=memory.total --format=csv,noheader 2>/dev/null | head -1)
    ok "nvidia-smi found: $GPU_NAME ($GPU_VRAM)"
else
    warn "nvidia-smi not found"
    echo ""
    echo -e "  ${YELLOW}To install NVIDIA drivers:${RESET}"
    echo -e "  ${DIM}sudo apt-get update${RESET}"
    echo -e "  ${DIM}sudo apt-get install -y nvidia-driver firmware-misc-nonfree${RESET}"
    echo -e "  ${DIM}sudo reboot${RESET}"
    echo ""
    echo -e "  ${DIM}Continuing without GPU — CPU inference will work fine.${RESET}"
    log "NVIDIA driver not installed, continuing with CPU"
fi

# ── 3. Python ─────────────────────────────────────────────────
section "3. Python"

PYTHON=""
for candidate in python3.11 python3.12 python3.13 python3; do
    if command -v "$candidate" &> /dev/null; then
        PY_VER=$("$candidate" --version 2>&1 | awk '{print $2}')
        PY_MAJOR=$(echo "$PY_VER" | cut -d. -f1)
        PY_MINOR=$(echo "$PY_VER" | cut -d. -f2)
        if [ "$PY_MAJOR" -ge 3 ] && [ "$PY_MINOR" -ge 11 ]; then
            PYTHON="$candidate"
            break
        fi
    fi
done

if [ -z "$PYTHON" ]; then
    warn "Python 3.11+ not found. Installing..."
    sudo apt-get update -qq
    sudo apt-get install -y python3.11 python3.11-venv python3.11-dev
    PYTHON="python3.11"
fi

PY_VER=$("$PYTHON" --version 2>&1)
ok "$PY_VER"

# ── 4. Virtual Environment ────────────────────────────────────
section "4. Virtual Environment"

if [ ! -d ".venv" ]; then
    log "Creating virtual environment..."
    "$PYTHON" -m venv .venv
    ok "Created .venv"
else
    ok ".venv already exists"
fi

# shellcheck disable=SC1091
source .venv/bin/activate
log "Activated .venv: $(which python)"

echo -e "  ${DIM}Installing dependencies...${RESET}"
pip install --quiet --upgrade pip
pip install --quiet -r requirements.txt 2>&1 | tee -a "$LOGFILE"

# Verify key imports
python -c "import fastapi, faiss, sentence_transformers, ollama" 2>/dev/null \
    && ok "All Python packages verified" \
    || die "Some packages failed to import. Check $LOGFILE"

# ── 5. Ollama ─────────────────────────────────────────────────
section "5. Ollama"

if ! command -v ollama &> /dev/null; then
    warn "Ollama not installed. Installing..."
    curl -fsSL https://ollama.com/install.sh | sh 2>&1 | tee -a "$LOGFILE"
fi

# Start Ollama if not already running
if ! curl -sf http://localhost:11434/api/tags &> /dev/null; then
    log "Starting Ollama server..."
    nohup ollama serve >> "$LOGFILE" 2>&1 &
    echo -e "  ${DIM}Waiting for Ollama to start...${RESET}"
    for i in $(seq 1 15); do
        if curl -sf http://localhost:11434/api/tags &> /dev/null; then
            break
        fi
        sleep 1
    done
fi

if curl -sf http://localhost:11434/api/tags &> /dev/null; then
    ok "Ollama server running on port 11434"
else
    die "Ollama failed to start after 15 seconds"
fi

# ── 6. Model Download ─────────────────────────────────────────
section "6. Model: $MODEL"

if ollama list 2>/dev/null | grep -q "$MODEL"; then
    ok "$MODEL already downloaded"
else
    echo -e "  ${DIM}Pulling $MODEL (this may take a few minutes)...${RESET}"
    ollama pull "$MODEL" 2>&1 | tee -a "$LOGFILE"
    ok "$MODEL downloaded"
fi

MODEL_SIZE=$(ollama list 2>/dev/null | grep "$MODEL" | awk '{print $3, $4}' || echo "unknown")
echo -e "  Size: ${CYAN}${MODEL_SIZE}${RESET}"

# ── 7. Generate Data & Build Index ────────────────────────────
section "7. Data & FAISS Index"

if [ ! -f "data/raw/courses.json" ]; then
    echo -e "  ${DIM}Generating synthetic data...${RESET}"
    python -m src.data.generator 2>&1 | tee -a "$LOGFILE"
    ok "Data generated"
else
    COURSE_COUNT=$(python -c "import json; print(len(json.load(open('data/raw/courses.json'))))")
    ok "data/raw/ exists ($COURSE_COUNT courses)"
fi

if [ ! -f "data/processed/faiss.index" ] || [ "data/raw/courses.json" -nt "data/processed/faiss.index" ]; then
    echo -e "  ${DIM}Building FAISS index...${RESET}"
    python -m scripts.build_index 2>&1 | tee -a "$LOGFILE"
    ok "FAISS index built"
else
    INDEX_SIZE=$(du -h data/processed/faiss.index | awk '{print $1}')
    ok "FAISS index exists ($INDEX_SIZE)"
fi

# Verify index is not empty
INDEX_KB=$(du -k data/processed/faiss.index | awk '{print $1}')
if [ "$INDEX_KB" -lt 10 ]; then
    die "FAISS index is suspiciously small (${INDEX_KB}KB). Rebuild with: python -m scripts.build_index"
fi

# ── 8. Verification Checklist ─────────────────────────────────
section "8. Final Verification"

PASS=0
TOTAL=0

check() {
    TOTAL=$((TOTAL + 1))
    if eval "$1" &> /dev/null; then
        ok "$2"
        PASS=$((PASS + 1))
    else
        fail "$2"
    fi
}

check "command -v nvidia-smi"                          "NVIDIA driver installed"
check "python --version"                               "Python $(python --version 2>&1 | awk '{print $2}')"
check "python -c 'import fastapi'"                     "FastAPI importable"
check "python -c 'import faiss'"                       "FAISS importable"
check "python -c 'import sentence_transformers'"       "sentence-transformers importable"
check "python -c 'import ollama'"                      "Ollama Python client importable"
check "curl -sf http://localhost:11434/api/tags"       "Ollama server responding"
check "ollama list 2>/dev/null | grep -q '$MODEL'"     "$MODEL available"
check "test -f data/raw/courses.json"                  "courses.json exists"
check "test -f data/raw/students.json"                 "students.json exists"
check "test -f data/processed/faiss.index"             "faiss.index exists"
check "python -c 'from src.api.main import app'"       "FastAPI app imports"
check "python -c 'from src.engine.recommender import Recommender'" "Recommender imports"

echo ""
echo -e "  ─────────────────────────────"
echo -e "  Results: ${GREEN}${PASS}${RESET}/${TOTAL} checks passed"
echo ""

if [ "$PASS" -eq "$TOTAL" ]; then
    echo -e "${GREEN}╔═══════════════════════════════════════════════╗${RESET}"
    echo -e "${GREEN}║  AcademIA is ready!                           ║${RESET}"
    echo -e "${GREEN}║                                               ║${RESET}"
    echo -e "${GREEN}║  CLI:  python demo/cli.py                     ║${RESET}"
    echo -e "${GREEN}║  Web:  uvicorn src.api.main:app --reload      ║${RESET}"
    echo -e "${GREEN}║        → http://localhost:8000                 ║${RESET}"
    echo -e "${GREEN}╚═══════════════════════════════════════════════╝${RESET}"
else
    echo -e "${YELLOW}Setup incomplete. ${PASS}/${TOTAL} passed.${RESET}"
    echo -e "${DIM}Check setup.log for details.${RESET}"
fi

log "Setup finished: $PASS/$TOTAL checks passed"
