from __future__ import annotations
from typing import List, Dict, Any, Tuple
import os

from chromadb import PersistentClient
from chromadb.utils import embedding_functions

def get_client(persist_dir: str) -> PersistentClient:
    os.makedirs(persist_dir, exist_ok=True)
    return PersistentClient(path=persist_dir)

def get_collection(client: PersistentClient, name: str, embedding_model: str):
    ef = embedding_functions.SentenceTransformerEmbeddingFunction(model_name=embedding_model)
    return client.get_or_create_collection(
        name=name,
        embedding_function=ef,
        metadata={"hnsw:space": "cosine"},
    )

def upsert_chunks(collection, chunks: List[tuple[str, Dict[str, Any]]], ids: List[str]):
    documents = [c[0] for c in chunks]
    metadatas = [c[1] for c in chunks]
    collection.upsert(ids=ids, documents=documents, metadatas=metadatas)

def query(collection, query_text: str, top_k: int = 4):
    res = collection.query(query_texts=[query_text], n_results=top_k, include=["documents", "metadatas", "distances"])
    docs = res.get("documents", [[]])[0]
    metas = res.get("metadatas", [[]])[0]
    dists = res.get("distances", [[]])[0]
    out = []
    for doc, meta, dist in zip(docs, metas, dists):
        out.append({"text": doc, "meta": meta, "distance": dist})
    return out
