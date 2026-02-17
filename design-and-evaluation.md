# Design & Evaluation — AddisTech Solutions Policy RAG

## 1) Design Goals
- Provide accurate answers **grounded** in a small policy corpus.
- Provide **citation transparency** (source filenames + supporting snippets).
- Keep the system lightweight, reproducible, and easy to run locally.

## 2) Architecture Overview
**Flow:** Documents → chunking → embeddings → Chroma → top-k retrieval → prompt injection → LLM answer (or extractive fallback).

### Components
- **Parser/Ingestion:** `scripts/ingest.py`
- **Chunking:** `app/chunking.py` (Markdown-aware: splits by headings then uses deterministic windows)
- **Embeddings:** SentenceTransformers `all-MiniLM-L6-v2` (free, local)
- **Vector Store:** Chroma (local persistent)
- **API/Web:** FastAPI (`/`, `/chat`, `/health`)
- **RAG Orchestration:** minimal custom pipeline (keeps dependencies small)

## 3) Key Design Choices (and why)
### Embedding model
- `sentence-transformers/all-MiniLM-L6-v2`
- Rationale: free/local, fast, widely used baseline for semantic search.

### Chunking
- Target window: ~500 tokens with ~100 overlap (approx via word windows)
- Rationale: preserves enough context for policy clauses while keeping retrieval precise.
- Headings are included at the top of each chunk to improve interpretability and citations.

### Retrieval (k)
- Default `k=4` (configurable via `TOP_K`)
- Rationale: small corpus; 4 typically captures the relevant sections without excessive noise.

### Prompt strategy + guardrails
- “Answer only from context” rule
- Refuse out-of-corpus questions
- Word limit (`MAX_ANSWER_WORDS`, default 200)
- Always list citations by source filename

### LLM provider
- OpenAI-compatible API via `openai` SDK (supports OpenAI, OpenRouter, Groq, etc.)
- If no API key: deterministic extractive fallback with citations to maintain usability.

## 4) Evaluation Plan
### Dataset
- 25 questions in `evaluation/questions.jsonl` covering PTO, remote work, security, expenses, holidays, travel, equipment, performance, benefits.

### Required metrics (per assignment)
1. **Groundedness**: % answers fully supported by retrieved evidence.
2. **Citation accuracy**: % answers whose citations point to correct supporting passages.
3. **Latency**: p50/p95 latency over 10–20 queries (we run 25).

### How to run
1) Ingest:
```bash
python scripts/ingest.py
```
2) Evaluate:
```bash
python scripts/evaluate.py
```

Outputs:
- `evaluation/eval_results.csv` for manual scoring of groundedness & citation accuracy.
- Console prints p50/p95 latency.

## 5) Results (fill after running)
After running `scripts/evaluate.py`, paste:
- p50 latency:
- p95 latency:
- Groundedness (%):
- Citation accuracy (%):

(If you use an LLM judge, note which model and rubric; otherwise document manual review procedure.)

