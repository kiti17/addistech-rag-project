from __future__ import annotations

from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from pydantic import BaseModel

from .rag import answer as rag_answer
from .config import settings

app = FastAPI(title="AddisTech Solutions Policy RAG", version="1.0.0")


class ChatRequest(BaseModel):
    question: str


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/debug/llm")
def debug_llm():
    # Does NOT return the actual API key, only whether it's present.
    return {
        "llm_api_key_present": bool(getattr(settings, "llm_api_key", None)),
        "llm_base_url": getattr(settings, "llm_base_url", None),
        "llm_model": getattr(settings, "llm_model", None),
    }


@app.get("/", response_class=HTMLResponse)
def home():
    return """<!doctype html>
<html>
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <title>AddisTech Policy Assistant</title>
    <style>
      body { font-family: system-ui, -apple-system, Segoe UI, Roboto, Arial; margin: 2rem; max-width: 900px; }
      textarea { width: 100%; height: 90px; }
      pre { white-space: pre-wrap; background: #f6f6f6; padding: 1rem; border-radius: 8px; }
      .row { margin: 1rem 0; }
      .small { color: #444; font-size: 0.9rem; }
      .card { border: 1px solid #ddd; padding: 0.75rem 1rem; border-radius: 8px; margin: 0.5rem 0; }
      code { background: #f0f0f0; padding: 0.1rem 0.25rem; border-radius: 4px; }
      button { padding: 0.5rem 0.9rem; cursor: pointer; }
    </style>
  </head>
  <body>
    <h1>AddisTech Solutions — Policy Assistant</h1>
    <p class="small">
      Ask questions about the AddisTech policy corpus. Answers include citations and snippets.
      <br/>
      Debug: <a href="/debug/llm" target="_blank">/debug/llm</a>
    </p>

    <div class="row">
      <textarea id="q" placeholder="Example: How many PTO days per year?"></textarea>
    </div>

    <button id="askBtn" type="button">Ask</button>

    <h2>Answer</h2>
    <pre id="a">—</pre>

    <h2>Citations</h2>
    <div id="c"></div>

    <script>
      async function send() {
        const question = document.getElementById('q').value.trim();
        if (!question) return;

        document.getElementById('a').textContent = "Loading...";
        document.getElementById('c').innerHTML = "";

        try {
          // Use RELATIVE URL so it works on any port (8000/8010/etc.)
          const res = await fetch('/chat', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({ question })
          });

          const text = await res.text();
          if (!res.ok) {
            document.getElementById('a').textContent = `HTTP ${res.status}\\n\\n${text}`;
            return;
          }

          const data = JSON.parse(text);
          document.getElementById('a').textContent =
            (data.answer || "(no answer field returned)") + "\\n\\nLatency: " + data.latency_ms + " ms";

          const c = document.getElementById('c');
          (data.citations || []).forEach(item => {
            const div = document.createElement('div');
            div.className = 'card';
            div.innerHTML =
              "<b>" + (item.source || "") + "</b>" +
              (item.section ? " — <code>" + item.section + "</code>" : "") +
              "<div class='small' style='margin-top:0.35rem'>" + (item.snippet || "") + "</div>";
            c.appendChild(div);
          });
        } catch (err) {
          document.getElementById('a').textContent = "Request failed:\\n" + err;
        }
      }

      document.getElementById('askBtn').addEventListener('click', send);
      document.getElementById('q').addEventListener('keydown', (e) => {
        if (e.ctrlKey && e.key === 'Enter') send();
      });
    </script>
  </body>
</html>"""


from fastapi import HTTPException
import traceback

@app.post("/chat")
async def chat(req: dict):
    try:
        question = req.get("question", "")
        return await rag_answer(question)  # or rag_answer(question)
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))