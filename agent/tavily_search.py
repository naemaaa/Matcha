"""
tavily_search.py — Web Search via Tavily untuk Matcha
Dijalankan paralel dengan Chroma query untuk memperkaya konteks LLM.
Scope: Indonesia only.
"""

import os
from typing import List, Dict, Optional
from concurrent.futures import ThreadPoolExecutor, as_completed

from tavily import TavilyClient

# ─────────────────────────────────────────────
# Init
# ─────────────────────────────────────────────

_tavily: Optional[TavilyClient] = None


def _get_client() -> TavilyClient:
    global _tavily
    if _tavily is None:
        api_key = os.environ.get("TAVILY_API_KEY", "")
        if not api_key:
            raise ValueError("TAVILY_API_KEY belum di-set di environment variable.")
        _tavily = TavilyClient(api_key=api_key)
    return _tavily


# ─────────────────────────────────────────────
# Search Functions
# ─────────────────────────────────────────────

def search_job_requirements(target_role: str) -> str:
    """
    Cari skill dan requirement terkini untuk target role di pasar kerja Indonesia.
    """
    client = _get_client()
    query = (
        f"skill yang dibutuhkan untuk menjadi {target_role} di Indonesia 2024 2025 "
        f"requirement lowongan kerja Glints Jobstreet LinkedIn"
    )
    try:
        results = client.search(
            query=query,
            search_depth="basic",
            max_results=3,
            include_domains=[
                "glints.com", "jobstreet.co.id", "linkedin.com",
                "kalibrr.com", "dicoding.com", "revou.co",
            ],
        )
        return _format_results(results.get("results", []), label="Info Pasar Kerja")
    except Exception as e:
        return f"[Tavily job search error: {e}]"


def search_learning_resources(target_role: str, skill_gaps: List[str]) -> str:
    """
    Cari kursus dan sumber belajar untuk skill gap di platform Indonesia.
    """
    client = _get_client()
    skills_str = ", ".join(skill_gaps[:5]) if skill_gaps else target_role
    query = (
        f"kursus belajar {skills_str} untuk {target_role} Indonesia "
        f"Dicoding RevoU Sanbercode Coursera rekomendasi terbaik"
    )
    try:
        results = client.search(
            query=query,
            search_depth="basic",
            max_results=3,
            include_domains=[
                "dicoding.com", "revou.co", "sanbercode.com",
                "coursera.org", "udemy.com", "buildwithangga.com",
                "codepolitan.com", "digitalskola.com",
            ],
        )
        return _format_results(results.get("results", []), label="Sumber Belajar Online")
    except Exception as e:
        return f"[Tavily course search error: {e}]"


def search_career_insights(target_role: str) -> str:
    """
    Cari info karir, gaji, dan prospek untuk role di Indonesia.
    """
    client = _get_client()
    query = (
        f"prospek karir {target_role} Indonesia gaji salary range 2024 2025 "
        f"tips sukses jenjang karir"
    )
    try:
        results = client.search(
            query=query,
            search_depth="basic",
            max_results=2,
        )
        return _format_results(results.get("results", []), label="Insight Karir")
    except Exception as e:
        return f"[Tavily career search error: {e}]"


# ─────────────────────────────────────────────
# Parallel Search
# ─────────────────────────────────────────────

def search_all_parallel(
    target_role: str,
    skill_gaps: List[str],
    include_career_insights: bool = False,
) -> Dict[str, str]:
    """
    Jalankan semua search secara paralel.
    Return dict: {job_requirements, learning_resources, career_insights}
    """
    tasks = {
        "job_requirements":   lambda: search_job_requirements(target_role),
        "learning_resources": lambda: search_learning_resources(target_role, skill_gaps),
    }
    if include_career_insights:
        tasks["career_insights"] = lambda: search_career_insights(target_role)

    results = {}
    with ThreadPoolExecutor(max_workers=len(tasks)) as executor:
        futures = {executor.submit(fn): key for key, fn in tasks.items()}
        for future in as_completed(futures):
            key = futures[future]
            try:
                results[key] = future.result()
            except Exception as e:
                results[key] = f"[Error: {e}]"

    return results


def format_tavily_results_for_prompt(tavily_results: Dict[str, str]) -> str:
    """Gabungkan semua hasil Tavily jadi satu blok teks untuk prompt LLM."""
    if not tavily_results:
        return ""
    sections = []
    for key, content in tavily_results.items():
        if content and not content.startswith("[Error") and not content.startswith("[Tavily"):
            sections.append(content)
    return "\n\n".join(sections)


# ─────────────────────────────────────────────
# Helper
# ─────────────────────────────────────────────

def _format_results(results: list, label: str) -> str:
    """Format hasil Tavily jadi teks ringkas untuk prompt."""
    if not results:
        return ""
    lines = [f"[{label}]"]
    for r in results:
        title   = r.get("title", "")
        url     = r.get("url", "")
        content = r.get("content", "")[:300]  # trim biar ga terlalu panjang
        lines.append(f"- {title} ({url})\n  {content}")
    return "\n".join(lines)