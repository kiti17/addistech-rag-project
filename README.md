# AddisTech Solutions — Policy RAG Assistant

This repo contains a Retrieval-Augmented Generation (RAG) application that answers user questions about a small corpus of **AddisTech Solutions** company policies and procedures.

## Requirements (per assignment)
- Local ingestion + indexing into a lightweight vector DB (Chroma)
- RAG pipeline with top-k retrieval, citations, and basic guardrails
- Web app with:
  - `/` chat UI
  - `/chat` API (POST)
  - `/health` status endpoint
- CI workflow on push/PR
- Evaluation questions + latency reporting

## Quickstart (Local)

### 1) Create venv + install deps
```bash
python -m venv .venv
# Windows:
#   .venv\Scripts\activate
# macOS/Linux:
#   source .venv/bin/activate

pip install -r requirements.txt
```

### 2) Ingest the corpus into Chroma
```bash
python scripts/ingest.py
```

This creates a local persistent DB in `./chroma_db/`.

### 3) Run the web app
```bash
uvicorn app.main:app --reload --port 8000
```

Open:
- http://127.0.0.1:8000/  (chat UI)
- http://127.0.0.1:8000/health
- POST http://127.0.0.1:8000/chat

## LLM Configuration (Optional but recommended)
If you set `LLM_API_KEY`, the app will use an OpenAI-compatible Chat Completions API.

Environment variables:
- `LLM_API_KEY` (required to enable LLM calls)
- `LLM_BASE_URL` (default: https://api.openai.com/v1)
- `LLM_MODEL` (default: gpt-4o-mini)
- `TOP_K` (default: 4)

Examples:

### OpenRouter
```bash
export LLM_API_KEY="..."
export LLM_BASE_URL="https://openrouter.ai/api/v1"
export LLM_MODEL="openai/gpt-4o-mini"
```

### Groq (OpenAI-compatible)
```bash
export LLM_API_KEY="..."
export LLM_BASE_URL="https://api.groq.com/openai/v1"
export LLM_MODEL="llama-3.1-70b-versatile"
```

If you do **not** set an API key, the app returns an extractive, citation-backed fallback response (still with retrieval + citations).

## Evaluation
Run:
```bash
python scripts/evaluate.py
```

Outputs:
- `evaluation/eval_results.csv` (includes latency per question + a citation-accuracy heuristic column)
- Prints p50/p95 latency to the console

Groundedness and exact citation accuracy can be filled manually in the CSV (the scaffold is included).

## Repo Contents
- `data/policies/` — policy corpus (Markdown)
- `scripts/ingest.py` — builds vector index
- `app/` — FastAPI web app + RAG pipeline
- `evaluation/questions.jsonl` — 25-question eval set
- `scripts/evaluate.py` — runs eval + latency stats
- `.github/workflows/ci.yml` — CI on push/PR
- `design-and-evaluation.md`, `ai-tooling.md` — submission docs

