from __future__ import annotations
import json, time, statistics, csv, os
import asyncio

from app.rag import answer as rag_answer

QUESTIONS_PATH = "evaluation/questions.jsonl"
OUT_PATH = "evaluation/eval_results.csv"

def load_questions(path: str):
    qs = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                qs.append(json.loads(line))
    return qs

def heuristic_citation_accuracy(expected_sources: list[str], citations: list[dict]) -> str:
    # Simple heuristic: did we cite at least one expected source?
    cited = {c.get("source") for c in (citations or [])}
    return "pass" if any(s in cited for s in expected_sources) else "fail"

async def run():
    qs = load_questions(QUESTIONS_PATH)
    latencies = []
    rows = []
    for q in qs:
        t0 = time.perf_counter()
        res = await rag_answer(q["question"])
        t1 = time.perf_counter()
        lat_ms = (t1 - t0) * 1000.0
        latencies.append(lat_ms)

        cit_acc = heuristic_citation_accuracy(q["expected_sources"], res.get("citations", []))

        rows.append({
            "id": q["id"],
            "question": q["question"],
            "gold": q["gold"],
            "expected_sources": ";".join(q["expected_sources"]),
            "answer": res.get("answer",""),
            "citations": ";".join(sorted({c.get("source","") for c in res.get("citations", [])})),
            "latency_ms": round(lat_ms, 2),
            "citation_accuracy_heuristic": cit_acc,
            "groundedness_manual": "",  # fill in manually after reviewing context vs answer
            "citation_accuracy_manual": "",  # optional manual score
            "notes": "",
        })

    p50 = statistics.median(latencies)
    p95 = statistics.quantiles(latencies, n=20)[18] if len(latencies) >= 20 else sorted(latencies)[int(0.95*(len(latencies)-1))]
    print(f"Latency p50={p50:.2f}ms p95={p95:.2f}ms over {len(latencies)} queries")

    os.makedirs(os.path.dirname(OUT_PATH), exist_ok=True)
    with open(OUT_PATH, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)
    print(f"Wrote {OUT_PATH}")

if __name__ == "__main__":
    asyncio.run(run())
