"""
ingest_chroma.py — Populate ChromaDB dari dataset JSON Matcha
Jalankan sekali: python -m agent.ingest_chroma

Collections yang dibuat:
- matcha_jobs     : 188 job postings
- matcha_courses  : 349 kursus
- matcha_keywords : 85 skill + keywords belajar
"""

import json
import os
import time
from pathlib import Path

import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer

# ─────────────────────────────────────────────
# Config
# ─────────────────────────────────────────────

CHROMA_PATH = os.environ.get("CHROMA_PATH", "/Users/macmini/matcha/chroma_db")
DATA_DIR    = os.environ.get("MATCHA_DATA_DIR", str(Path(__file__).parent / "data"))

EMBED_MODEL = "BAAI/bge-large-en-v1.5"

JOBS_PATH     = os.path.join(DATA_DIR, "all_jobs_fixed.json")
COURSES_PATH  = os.path.join(DATA_DIR, "course_catalog.json")
KEYWORDS_PATH = os.path.join(DATA_DIR, "keyword_per_skill.json")


# ─────────────────────────────────────────────
# Init
# ─────────────────────────────────────────────

def load_json(path: str):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def build_text_for_job(job: dict) -> str:
    skills = ", ".join(job.get("skills_required", []))
    desc   = job.get("description_raw", "")[:400]  # trim biar ga kebanyakan token
    return (
        f"Role: {job.get('role', '')} | "
        f"Level: {job.get('level', '')} | "
        f"Skills: {skills} | "
        f"Description: {desc}"
    )


def build_text_for_course(course: dict) -> str:
    skills = ", ".join(course.get("skills_covered", []))
    return (
        f"Title: {course.get('title', '')} | "
        f"Platform: {course.get('platform', '')} | "
        f"Level: {course.get('level', '')} | "
        f"Skills: {skills}"
    )


def build_text_for_keyword(item: dict) -> str:
    queries = " | ".join(
        kw.get("query", "") for kw in item.get("keywords", [])
    )
    return f"Skill: {item.get('skill', '')} | Keywords: {queries}"


# ─────────────────────────────────────────────
# Ingest
# ─────────────────────────────────────────────

def ingest_collection(
    collection,
    items: list,
    text_fn,
    id_field: str,
    model: SentenceTransformer,
    batch_size: int = 32,
):
    """Embed dan insert items ke collection dalam batch."""
    ids, texts, metadatas = [], [], []

    for item in items:
        item_id = str(item.get(id_field, "")) or str(hash(json.dumps(item)))
        text    = text_fn(item)
        # Simpan semua field sebagai metadata (kecuali description_raw yang panjang)
        meta = {k: (v if isinstance(v, (str, int, float, bool)) else json.dumps(v, ensure_ascii=False))
                for k, v in item.items() if k != "description_raw"}
        ids.append(item_id)
        texts.append(text)
        metadatas.append(meta)

    # Embed dalam batch
    total = len(texts)
    print(f"  Embedding {total} items...")
    for i in range(0, total, batch_size):
        batch_ids   = ids[i:i+batch_size]
        batch_texts = texts[i:i+batch_size]
        batch_meta  = metadatas[i:i+batch_size]

        # BGE model butuh prefix "Represent this sentence: " untuk passage
        prefixed = [f"Represent this sentence: {t}" for t in batch_texts]
        embeddings = model.encode(prefixed, normalize_embeddings=True).tolist()

        collection.add(
            ids=batch_ids,
            embeddings=embeddings,
            documents=batch_texts,
            metadatas=batch_meta,
        )
        print(f"  [{i+len(batch_ids)}/{total}] inserted")
        time.sleep(0.1)  # hindari throttle CPU


def main():
    print(f"Loading embedding model: {EMBED_MODEL}")
    model = SentenceTransformer(EMBED_MODEL)
    print("Model loaded.\n")

    print(f"Connecting to ChromaDB at: {CHROMA_PATH}")
    client = chromadb.PersistentClient(
        path=CHROMA_PATH,
        settings=Settings(anonymized_telemetry=False),
    )

    # ── Jobs ──
    print("\n[1/3] Ingesting matcha_jobs...")
    jobs = load_json(JOBS_PATH)
    col_jobs = client.get_or_create_collection(
        name="matcha_jobs",
        metadata={"hnsw:space": "cosine"},
    )
    if col_jobs.count() == 0:
        ingest_collection(col_jobs, jobs, build_text_for_job, "id", model)
        print(f"  Done: {col_jobs.count()} documents")
    else:
        print(f"  Skipped (already has {col_jobs.count()} docs)")

    # ── Courses ──
    print("\n[2/3] Ingesting matcha_courses...")
    courses = load_json(COURSES_PATH)
    col_courses = client.get_or_create_collection(
        name="matcha_courses",
        metadata={"hnsw:space": "cosine"},
    )
    if col_courses.count() == 0:
        ingest_collection(col_courses, courses, build_text_for_course, "id", model)
        print(f"  Done: {col_courses.count()} documents")
    else:
        print(f"  Skipped (already has {col_courses.count()} docs)")

    # ── Keywords ──
    print("\n[3/3] Ingesting matcha_keywords...")
    keywords = load_json(KEYWORDS_PATH)
    # keyword_per_skill ga punya field id, buat dari skill name
    for item in keywords:
        item["id"] = f"kw_{item['skill'].lower().replace(' ', '_').replace('/', '_')}"
    col_keywords = client.get_or_create_collection(
        name="matcha_keywords",
        metadata={"hnsw:space": "cosine"},
    )
    if col_keywords.count() == 0:
        ingest_collection(col_keywords, keywords, build_text_for_keyword, "id", model)
        print(f"  Done: {col_keywords.count()} documents")
    else:
        print(f"  Skipped (already has {col_keywords.count()} docs)")

    print("\n✅ Ingest selesai!")
    print(f"   matcha_jobs:     {col_jobs.count()} docs")
    print(f"   matcha_courses:  {col_courses.count()} docs")
    print(f"   matcha_keywords: {col_keywords.count()} docs")


if __name__ == "__main__":
    main()