# AI Tooling Summary

This project was built with assistance from AI code-generation and editing tools.

## Tools Used
- ChatGPT (OpenAI): architecture planning, code scaffolding, debugging assistance, and documentation templates.
- (Optional) GitHub Copilot / IDE autocomplete: small refactors and boilerplate generation.

## How AI Tools Were Used
- **Scaffolding:** generated initial FastAPI endpoints (`/`, `/chat`, `/health`) and RAG pipeline structure.
- **Chunking + ingestion:** drafted deterministic chunking logic and Chroma ingestion script.
- **Prompting:** iterated on prompt rules to enforce grounded answers and consistent citations.
- **Evaluation:** generated an initial evaluation set (25 questions) and a CSV-based evaluation runner.

## What Worked Well
- Rapid generation of consistent boilerplate code and repo structure.
- Faster iteration on prompt guardrails and JSON response formats.
- Quick creation of a diverse evaluation question set aligned to the corpus.

## What Didn’t Work Well / Needed Manual Work
- Manual review was still required for **groundedness** and **citation accuracy** scoring.
- Some AI-generated chunking/token heuristics needed human judgement to keep behavior stable and interpretable.
- Deployment and environment settings still required hands-on verification (keys, host settings, and start commands).

## Human Verification Steps
- Ran ingestion and confirmed Chroma DB was populated with expected chunk counts.
- Manually tested queries in the UI and verified citations matched the correct policy files.
- Reviewed evaluation outputs and documented results in `design-and-evaluation.md`.
