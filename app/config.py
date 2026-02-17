from __future__ import annotations
from pydantic import BaseModel
import os

class Settings(BaseModel):
    # Paths
    policies_dir: str = os.getenv("POLICIES_DIR", "data/policies")
    chroma_dir: str = os.getenv("CHROMA_DIR", "chroma_db")

    # Retrieval
    top_k: int = int(os.getenv("TOP_K", "4"))
    max_answer_words: int = int(os.getenv("MAX_ANSWER_WORDS", "200"))

    # Embeddings
    embedding_model: str = os.getenv("EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2")

    # LLM (OpenAI-compatible)
    llm_api_key: str | None = os.getenv("LLM_API_KEY")
    llm_base_url: str = os.getenv("LLM_BASE_URL", "https://api.openai.com/v1")
    llm_model: str = os.getenv("LLM_MODEL", "gpt-4o-mini")  # any OpenAI-compatible model works
    llm_timeout_s: int = int(os.getenv("LLM_TIMEOUT_S", "30"))

settings = Settings()
