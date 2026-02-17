from __future__ import annotations
from typing import List, Dict, Any, Optional
import os, textwrap

def build_prompt(question: str, contexts: List[Dict[str, Any]], max_words: int) -> str:
    # Provide compact context with explicit source markers for citations.
    ctx_lines = []
    for i, c in enumerate(contexts, start=1):
        src = c["meta"].get("source", "unknown")
        sec = c["meta"].get("section", "")
        ctx_lines.append(f"[{i}] SOURCE={src} SECTION={sec}\n{c['text']}".strip())
    ctx = "\n\n".join(ctx_lines)

    return textwrap.dedent(f"""    You are AddisTech Solutions' internal policy assistant.

    Rules:
    1) Answer ONLY using the provided context excerpts. Do not use outside knowledge.
    2) If the answer is not in the context, say: "I can only answer questions about AddisTech Solutions policies based on the provided documents."
    3) Keep the answer under {max_words} words.
    4) Always include a short Citations section listing the SOURCE filenames you relied on (no URLs).

    Context:
    {ctx}

    Question:
    {question}

    Write the answer in plain English with bullet points when appropriate.
    """).strip()

async def call_openai_compatible(prompt: str, *, api_key: str, base_url: str, model: str, timeout_s: int) -> str:
    # Uses the official OpenAI python package (works with OpenAI-compatible providers via base_url).
    from openai import AsyncOpenAI
    client = AsyncOpenAI(api_key=api_key, base_url=base_url, timeout=timeout_s)
    resp = await client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.2,
    )
    return resp.choices[0].message.content.strip()

def fallback_answer(question: str, contexts: list[dict], max_words: int) -> str:
    # Deterministic extractive fallback: returns top snippets + refusal if nothing relevant.
    if not contexts:
        return "I can only answer questions about AddisTech Solutions policies based on the provided documents."
    # Create a brief stitched response.
    bullets = []
    used_sources = []
    for c in contexts[:3]:
        src = c["meta"].get("source", "unknown")
        used_sources.append(src)
        snippet = c["text"].replace("\n", " ").strip()
        if len(snippet) > 220:
            snippet = snippet[:220].rstrip() + "..."
        bullets.append(f"- {snippet} ({src})")
    # Limit rough length by truncating bullets.
    body = "Here are the most relevant policy excerpts I found:\n" + "\n".join(bullets)
    citations = "Citations: " + ", ".join(sorted(set(used_sources)))
    out = body + "\n\n" + citations
    # Hard word cap (approx)
    words = out.split()
    if len(words) > max_words:
        out = " ".join(words[:max_words]).rstrip() + "…\n\n" + citations
    return out
