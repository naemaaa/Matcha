"""
chroma_client.py — Helper untuk query lokal ChromaDB di Matcha.

Berisi fungsi retrieval untuk job, course, keyword, dan skill recommendation.
"""

import os
from typing import Any, Dict, List, Optional

import chromadb
from chromadb.config import Settings

CHROMA_PATH = os.environ.get("CHROMA_PATH", "/Users/macmini/matcha/chroma_db")

COLLECTION_JOBS = "matcha_jobs"
COLLECTION_COURSES = "matcha_courses"
COLLECTION_KEYWORDS = "matcha_keywords"


def _get_client() -> chromadb.PersistentClient:
    return chromadb.PersistentClient(
        path=CHROMA_PATH,
        settings=Settings(anonymized_telemetry=False),
    )


def _get_collection(name: str):
    client = _get_client()
    return client.get_or_create_collection(name=name)


def _safe_query(collection, query_text: str, n_results: int = 5):
    try:
        return collection.query(
            query_texts=[query_text],
            n_results=n_results,
            include=["metadatas", "documents"],
        )
    except Exception:
        return {"metadatas": [[]], "documents": [[]]}


def get_required_skills_for_role(target_role: str, top_k: int = 8) -> List[str]:
    """Ambil skill teratas yang terkait dengan target role dari koleksi keyword."""
    collection = _get_collection(COLLECTION_KEYWORDS)
    query = f"skill yang diperlukan untuk menjadi {target_role}"
    query_result = _safe_query(collection, query, n_results=top_k)

    skills: List[str] = []
    metadatas = query_result.get("metadatas", [[]])[0]
    for meta in metadatas:
        if isinstance(meta, dict):
            skill = meta.get("skill")
            if skill:
                skills.append(skill)
        elif isinstance(meta, str) and meta:
            parts = meta.split("|")
            if parts:
                skills.append(parts[0].replace("Skill:", "").strip())
    return list(dict.fromkeys(skills))[:top_k]


def find_matching_jobs(target_role: str, current_skills: List[str], top_k: int = 3) -> List[Dict[str, Any]]:
    """Cari lowongan yang relevan dengan target role dan skill saat ini."""
    collection = _get_collection(COLLECTION_JOBS)
    query_text = target_role
    if current_skills:
        query_text += " " + " ".join(current_skills[:5])
    query_result = _safe_query(collection, query_text, n_results=top_k)

    jobs = []
    documents = query_result.get("documents", [[]])[0]
    metadatas = query_result.get("metadatas", [[]])[0]
    for doc, meta in zip(documents, metadatas):
        jobs.append({"document": doc, "metadata": meta})
    return jobs


def find_matching_courses(target_role: str, current_skills: List[str], top_k: int = 3) -> List[Dict[str, Any]]:
    """Cari kursus yang relevan dengan target role dan skill saat ini."""
    collection = _get_collection(COLLECTION_COURSES)
    query_text = target_role
    if current_skills:
        query_text += " " + " ".join(current_skills[:5])
    query_result = _safe_query(collection, query_text, n_results=top_k)

    courses = []
    documents = query_result.get("documents", [[]])[0]
    metadatas = query_result.get("metadatas", [[]])[0]
    for doc, meta in zip(documents, metadatas):
        courses.append({"document": doc, "metadata": meta})
    return courses


def get_keywords_for_skills(skills: List[str], top_k: int = 5) -> Dict[str, List[str]]:
    """Ambil keyword relevan dari koleksi skill untuk daftar skill tertentu."""
    if not skills:
        return {}

    collection = _get_collection(COLLECTION_KEYWORDS)
    query_text = " ".join(skills[:5])
    query_result = _safe_query(collection, query_text, n_results=top_k)

    keywords: Dict[str, List[str]] = {}
    metadatas = query_result.get("metadatas", [[]])[0]
    for meta in metadatas:
        if isinstance(meta, dict):
            skill = meta.get("skill")
            query_keywords = meta.get("keywords")
            if skill and isinstance(query_keywords, list):
                keywords[skill] = query_keywords
    return keywords


def format_jobs_for_prompt(jobs: List[Dict[str, Any]]) -> str:
    """Format hasil job matching agar mudah dibaca oleh prompt LLM."""
    if not jobs:
        return ""

    lines = []
    for idx, item in enumerate(jobs, 1):
        meta = item.get("metadata", {}) or {}
        doc = item.get("document", "")
        role = meta.get("role") or meta.get("title") or ""
        level = meta.get("level", "")
        skills = meta.get("skills_required") or meta.get("skills") or ""
        company = meta.get("company", "")
        lines.append(
            f"[{idx}] Role: {role} | Level: {level} | Company: {company} | Skills: {skills}\nDescription: {doc}"
        )
    return "\n\n".join(lines)


def format_courses_for_prompt(courses: List[Dict[str, Any]]) -> str:
    """Format hasil course matching agar mudah dibaca oleh prompt LLM."""
    if not courses:
        return ""

    lines = []
    for idx, item in enumerate(courses, 1):
        meta = item.get("metadata", {}) or {}
        doc = item.get("document", "")
        title = meta.get("title") or meta.get("course_name") or ""
        platform = meta.get("platform", "")
        level = meta.get("level", "")
        lines.append(
            f"[{idx}] {title} | Platform: {platform} | Level: {level}\n{doc}"
        )
    return "\n\n".join(lines)
