from __future__ import annotations
import re
from dataclasses import dataclass
from typing import List, Dict, Any, Iterable

@dataclass
class Chunk:
    text: str
    metadata: Dict[str, Any]

_heading_re = re.compile(r"^(#{1,6})\s+(.*)$", re.MULTILINE)

def _approx_token_len(s: str) -> int:
    # Cheap approximation: 1 token ~= 4 chars (common heuristic). Deterministic and fast.
    return max(1, len(s) // 4)

def chunk_markdown(doc_text: str, source: str, chunk_tokens: int = 500, overlap_tokens: int = 100) -> List[Chunk]:
    # Split by headings to preserve structure for citation/snippets.
    # Then window each section with overlap.
    sections: List[tuple[str, str]] = []
    matches = list(_heading_re.finditer(doc_text))
    if not matches:
        sections = [("Document", doc_text)]
    else:
        for i, m in enumerate(matches):
            start = m.start()
            end = matches[i + 1].start() if i + 1 < len(matches) else len(doc_text)
            heading = m.group(0).strip()
            body = doc_text[m.end():end].strip()
            sections.append((heading, body))

    chunks: List[Chunk] = []
    for section_heading, body in sections:
        if not body:
            continue
        words = body.split()
        # Convert token budgets into word budgets using a stable ratio: ~0.75 words/token
        # This is a heuristic but deterministic.
        words_per_token = 0.75
        window_words = max(80, int(chunk_tokens * words_per_token))
        overlap_words = max(20, int(overlap_tokens * words_per_token))

        idx = 0
        while idx < len(words):
            window = words[idx: idx + window_words]
            text = f"{section_heading}\n\n" + " ".join(window)
            chunks.append(Chunk(
                text=text.strip(),
                metadata={
                    "source": source,
                    "section": section_heading,
                    "chunk_index": len(chunks),
                    "approx_tokens": _approx_token_len(text),
                }
            ))
            if idx + window_words >= len(words):
                break
            idx += max(1, window_words - overlap_words)

    return chunks
