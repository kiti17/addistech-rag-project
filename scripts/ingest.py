from __future__ import annotations
import os, glob, hashlib
from app.config import settings
from app.chunking import chunk_markdown
from app.vectorstore import get_client, get_collection, upsert_chunks

COLLECTION = "addistech_policies"

def stable_id(source: str, section: str, chunk_index: int, text: str) -> str:
    h = hashlib.sha1()
    h.update(source.encode("utf-8"))
    h.update(section.encode("utf-8"))
    h.update(str(chunk_index).encode("utf-8"))
    h.update(text.encode("utf-8"))
    return h.hexdigest()

def main():
    pol_dir = settings.policies_dir
    files = sorted(glob.glob(os.path.join(pol_dir, "*.md")))
    if not files:
        raise SystemExit(f"No policy .md files found in {pol_dir}")

    client = get_client(settings.chroma_dir)
    col = get_collection(client, COLLECTION, settings.embedding_model)

    all_chunks = []
    all_ids = []

    for fp in files:
        source = os.path.basename(fp)
        with open(fp, "r", encoding="utf-8") as f:
            text = f.read()

        chunks = chunk_markdown(text, source=source, chunk_tokens=500, overlap_tokens=100)
        for i, ch in enumerate(chunks):
            _id = stable_id(source, ch.metadata.get("section",""), i, ch.text)
            all_ids.append(_id)
            all_chunks.append((ch.text, ch.metadata))

    upsert_chunks(col, all_chunks, all_ids)
    print(f"Ingested {len(files)} files -> {len(all_chunks)} chunks into {settings.chroma_dir}/{COLLECTION}")

if __name__ == "__main__":
    main()
