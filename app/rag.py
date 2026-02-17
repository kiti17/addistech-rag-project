from __future__ import annotations
from typing import Dict, Any, List
import time

from .config import settings
from .vectorstore import get_client, get_collection, query as vs_query
from .llm import build_prompt, call_openai_compatible, fallback_answer

_COLLECTION = "addistech_policies"

def retrieve(question: str) -> List[Dict[str, Any]]:
    client = get_client(settings.chroma_dir)
    col = get_collection(client, _COLLECTION, settings.embedding_model)
    return vs_query(col, question, top_k=settings.top_k)

async def answer(question: str) -> Dict[str, Any]:
    t0 = time.perf_counter()
    contexts = retrieve(question)

    # Build citations/snippets for API response
    citations = []
    for c in contexts:
        src = c["meta"].get("source", "unknown")
        sec = c["meta"].get("section", "")
        snippet = c["text"].replace("\n", " ").strip()
        if len(snippet) > 260:
            snippet = snippet[:260].rstrip() + "..."
        citations.append({"source": src, "section": sec, "snippet": snippet})

    # Generate
    if settings.llm_api_key:
        prompt = build_prompt(question, contexts, settings.max_answer_words)
        text = await call_openai_compatible(
            prompt,
            api_key=settings.llm_api_key,
            base_url=settings.llm_base_url,
            model=settings.llm_model,
            timeout_s=settings.llm_timeout_s,
        )
    else:
        text = fallback_answer(question, contexts, settings.max_answer_words)

    latency_ms = (time.perf_counter() - t0) * 1000.0
    return {"answer": text, "citations": citations, "latency_ms": round(latency_ms, 2)}
