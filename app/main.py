from __future__ import annotations
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from pydantic import BaseModel

from .rag import answer as rag_answer

app = FastAPI(title="AddisTech Solutions Policy RAG", version="1.0.0")

class ChatRequest(BaseModel):
    question: str

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/", response_class=HTMLResponse)
def home():
    # Minimal chat UI to satisfy spec: input box -> POST /chat -> render response
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
    </style>
  </head>
  <body>
    <h1>AddisTech Solutions — Policy Assistant</h1>
    <p class="small">Ask questions about the AddisTech policy corpus. Answers include citations and snippets.</p>

    <div class="row">
      <textarea id="q" placeholder="Example: How many PTO days per year?"></textarea>
    </div>
    <button onclick="send()">Ask</button>

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

        const res = await fetch('/chat', {
          method: 'POST',
          headers: {'Content-Type': 'application/json'},
          body: JSON.stringify({question})
        });
        const data = await res.json();
        document.getElementById('a').textContent = data.answer + "\n\nLatency: " + data.latency_ms + " ms";

        const c = document.getElementById('c');
        (data.citations || []).forEach(item => {
          const div = document.createElement('div');
          div.className = 'card';
          div.innerHTML = "<b>" + item.source + "</b>" + (item.section ? " — <code>" + item.section + "</code>" : "") +
                          "<div class='small' style='margin-top:0.35rem'>" + item.snippet + "</div>";
          c.appendChild(div);
        });
      }
    </script>
  </body>
</html>"""

@app.post("/chat")
async def chat(req: ChatRequest):
    return await rag_answer(req.question)
