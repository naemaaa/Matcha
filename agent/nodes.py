"""
nodes.py — Semua Node Agent untuk Matcha (LangGraph)
Setiap fungsi adalah satu node yang menerima state dan mengembalikan state update.
"""

import json
import os
import re
from concurrent.futures import ThreadPoolExecutor
from typing import Dict, Any

from groq import Groq

from .state import MatchaState
from .prompts import (
    INTENT_CLASSIFIER_PROMPT,
    USER_PROFILER_PROMPT,
    SKILL_GAP_PROMPT,
    RESOURCE_RECOMMENDER_PROMPT,
    CV_REVIEWER_PROMPT,
    LINKEDIN_REVIEWER_PROMPT,
)
from .chroma_client import (
    get_required_skills_for_role,
    find_matching_courses,
    find_matching_jobs,
    get_keywords_for_skills,
    format_courses_for_prompt,
    format_jobs_for_prompt,
)
from agent import state
from .tavily_search import search_all_parallel, format_tavily_results_for_prompt

# ─────────────────────────────────────────────
# Setup LLM — Groq
# ─────────────────────────────────────────────
from dotenv import load_dotenv
load_dotenv()

_client = Groq(api_key=os.environ.get("GROQ_API_KEY", "")) 
GROQ_MODEL = "llama-3.3-70b-versatile"  # ganti sesuai model yang dipakai
print("DEBUG GROQ KEY:", os.environ.get("GROQ_API_KEY", "NOT FOUND")[:10])

def _call_llm(prompt: str) -> str:
    """Helper: panggil Groq dan kembalikan teks respons."""
    response = _client.chat.completions.create(
        model=GROQ_MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7,
        max_tokens=2048,
    )
    return response.choices[0].message.content.strip()


def _parse_json_response(text: str) -> Dict[str, Any]:
    """
    Helper: parse JSON dari respons LLM.
    Coba ekstrak blok JSON jika ada markdown code fence.
    """
    # Bersihkan markdown code fence kalau ada
    cleaned = re.sub(r"```(?:json)?\s*", "", text).replace("```", "").strip()
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        # Coba cari pola {...} pertama di teks
        match = re.search(r"\{.*\}", cleaned, re.DOTALL)
        if match:
            try:
                return json.loads(match.group())
            except json.JSONDecodeError:
                pass
    return {}


# ─────────────────────────────────────────────
# NODE 1: Intent Classifier
# ─────────────────────────────────────────────

def intent_classifier_node(state: MatchaState) -> MatchaState:
    """
    Mengklasifikasikan intent dari input user.
    Output: detected_intent, intent_confidence, extracted_info
    """
    user_input = state.get("user_input", "")

    prompt = INTENT_CLASSIFIER_PROMPT.format(user_input=user_input)

    try:
        raw = _call_llm(prompt)
        parsed = _parse_json_response(raw)

        intent = parsed.get("intent", "CAREER_EXPLORATION").upper()
        confidence = float(parsed.get("confidence", 0.7))
        extracted_info = parsed.get("extracted_info", {})
    except Exception:
        intent = "CAREER_EXPLORATION"
        confidence = 0.5
        extracted_info = {}

    # ── Drift Detection ──
    history: list = state.get("previous_intent_history", [])
    drift_detected = False

    # Jika ada 3+ intent terakhir dan intent sekarang berbeda jauh dari mayoritas
    if len(history) >= 3:
        recent = history[-3:]
        most_common = max(set(recent), key=recent.count)
        if intent != most_common and intent not in ("CONFIRMATION", "PUSH_BACK"):
            drift_detected = True

    updated_history = history + [intent]

    return {
        **state,
        "detected_intent": intent,
        "intent_confidence": confidence,
        "extracted_info": extracted_info,
        "drift_detected": drift_detected,
        "previous_intent_history": updated_history,
    }


# ─────────────────────────────────────────────
# NODE 2: User Profiler
# ─────────────────────────────────────────────

def user_profiler_node(state: MatchaState) -> MatchaState:
    """
    Membangun dan mengupdate profil karir user dari percakapan.
    Output: user_profile (di-merge dengan profil sebelumnya)
    """
    user_input = state.get("user_input", "")
    detected_intent = state.get("detected_intent", "")
    messages = state.get("messages", [])

    # Format chat history untuk prompt
    chat_history_text = "\n".join(
        f"{m['role'].upper()}: {m['content']}" for m in messages[-10:]  # max 10 pesan terakhir
    )

    prompt = USER_PROFILER_PROMPT.format(
        chat_history=chat_history_text,
        user_input=user_input,
        detected_intent=detected_intent,
    )
    print("DEBUG prompt:", prompt[:500])
    try:
        raw = _call_llm(prompt)
        print("DEBUG raw LLM response:", raw[:300])
        new_profile = _parse_json_response(raw)
        print("DEBUG parsed profile:", new_profile)
    except Exception as e:
        print("DEBUG ERROR user_profiler:", type(e).__name__, str(e))
        new_profile = {}

    # Merge dengan profil lama: hanya timpa field yang ada nilainya (bukan null)
    existing_profile = dict(state.get("user_profile") or {})
    for key, value in new_profile.items():
        if value is not None and value != [] and value != "":
            existing_profile[key] = value

    # Pastikan current_skills selalu list
    if "current_skills" not in existing_profile:
        existing_profile["current_skills"] = []

    print("DEBUG profile:", existing_profile)
    return {
        **state,
        "user_profile": existing_profile,
    }

    


# ─────────────────────────────────────────────
# NODE 3: Skill Gap Analyzer
# ─────────────────────────────────────────────

def skill_gap_analyzer_node(state: MatchaState) -> MatchaState:
    """
    Menganalisis skill gap dan menghasilkan learning path.
    Data dikumpulkan paralel dari Chroma (lokal) + Tavily (web).
    Output: skill_gaps (teks), agent_response
    """
    print("DEBUG skill_gap input profile:", state.get("user_profile"))
    user_profile    = state.get("user_profile") or {}
    detected_intent = state.get("detected_intent", "")

    if not user_profile.get("target_role"):
        return {
            **state,
            "agent_response": (
                "Untuk membuat learning path yang tepat, aku perlu tahu dulu "
                "target karir kamu. Kamu ingin berkarir sebagai apa? 🎯"
            ),
        }

    target_role    = user_profile.get("target_role", "")
    current_skills = user_profile.get("current_skills", [])

    # ── Paralel: Chroma + Tavily ──
    with ThreadPoolExecutor(max_workers=2) as executor:
        future_chroma = executor.submit(
            lambda: {
                "required_skills": get_required_skills_for_role(target_role),
                "matching_jobs":   find_matching_jobs(target_role, current_skills, top_k=3),
            }
        )
        future_tavily = executor.submit(
            search_all_parallel,
            target_role,
            current_skills,
            False,  # career insights off supaya hemat quota
        )
        chroma_data  = future_chroma.result()
        tavily_data  = future_tavily.result()

    tavily_context = format_tavily_results_for_prompt(tavily_data)

    enriched_profile = {
        **user_profile,
        "market_required_skills":  chroma_data["required_skills"][:15],
        "sample_job_requirements": format_jobs_for_prompt(chroma_data["matching_jobs"]),
        "web_context":             tavily_context,
    }

    prompt = SKILL_GAP_PROMPT.format(
        user_profile=json.dumps(enriched_profile, ensure_ascii=False, indent=2),
        detected_intent=detected_intent,
    )

    try:
        response_text = _call_llm(prompt)
    except Exception as e:
        response_text = f"Maaf, terjadi kendala saat menganalisis skill gap. Coba lagi ya! ({e})"

    return {
        **state,
        "skill_gaps":     response_text,
        "agent_response": response_text,
    }


# ─────────────────────────────────────────────
# NODE 4: CV Reviewer
# ─────────────────────────────────────────────

def cv_reviewer_node(state: MatchaState) -> MatchaState:
    """
    Mereview CV user dan memberikan feedback vs target karir.
    Output: agent_response
    """
    cv_text = state.get("cv_text", "")
    user_profile = state.get("user_profile") or {}
    skill_gaps = state.get("skill_gaps", "Belum dianalisis")

    if not cv_text:
        return {
            **state,
            "agent_response": (
                "Kamu belum upload CV-nya nih! Upload dulu di panel kiri atas ya, "
                "baru aku bisa kasih feedback yang spesifik. 📄"
            ),
        }

    target_role = user_profile.get("target_role", "belum ditentukan")

    prompt = CV_REVIEWER_PROMPT.format(
        cv_text=cv_text,
        target_role=target_role,
        skill_gaps=skill_gaps,
    )

    try:
        response_text = _call_llm(prompt)
    except Exception as e:
        response_text = f"Maaf, terjadi kendala saat review CV. Coba lagi ya! ({e})"

    return {
        **state,
        "agent_response": response_text,
    }


# ─────────────────────────────────────────────
# NODE 5: LinkedIn Reviewer
# ─────────────────────────────────────────────

def linkedin_reviewer_node(state: MatchaState) -> MatchaState:
    """
    Mereview profil LinkedIn user dan memberikan saran optimasi.
    Output: agent_response
    """
    linkedin_text = state.get("linkedin_text", "")
    user_profile = state.get("user_profile") or {}
    skill_gaps = state.get("skill_gaps", "Belum dianalisis")

    if not linkedin_text:
        return {
            **state,
            "agent_response": (
                "Kamu belum upload profil LinkedIn-nya nih! Export PDF dari LinkedIn "
                "(Me → Save to PDF) lalu upload di panel kiri atas ya. 💼"
            ),
        }

    target_role = user_profile.get("target_role", "belum ditentukan")

    prompt = LINKEDIN_REVIEWER_PROMPT.format(
        linkedin_text=linkedin_text,
        target_role=target_role,
        skill_gaps=skill_gaps,
    )

    try:
        response_text = _call_llm(prompt)
    except Exception as e:
        response_text = f"Maaf, terjadi kendala saat review LinkedIn. Coba lagi ya! ({e})"

    return {
        **state,
        "agent_response": response_text,
    }


# ─────────────────────────────────────────────
# NODE 6: General Responder
# Untuk intent yang tidak butuh analisis berat
# (PUSH_BACK, CONFIRMATION, CONSTRAINT_UPDATE)
# ─────────────────────────────────────────────

def general_responder_node(state: MatchaState) -> MatchaState:
    """
    Menangani intent umum: push back, konfirmasi, update constraint.
    Output: agent_response
    """
    user_input = state.get("user_input", "")
    detected_intent = state.get("detected_intent", "")
    user_profile = state.get("user_profile") or {}
    drift_detected = state.get("drift_detected", False)
    messages = state.get("messages", [])

    chat_history_text = "\n".join(
        f"{m['role'].upper()}: {m['content']}" for m in messages[-6:]
    )

    drift_note = ""
    if drift_detected:
        drift_note = (
            "\n\nCatatan: Aku mendeteksi kamu mungkin mengubah arah tujuan karir. "
            "Apakah kamu ingin aku memperbarui rencana belajarmu sesuai tujuan terbaru?"
        )

    prompt = f"""Kamu adalah Matcha, asisten karir adaptif yang ramah dan suportif dalam Bahasa Indonesia.

Riwayat percakapan:
{chat_history_text}

Intent user saat ini: {detected_intent}
Input terbaru user: {user_input}
Profil user: {json.dumps(user_profile, ensure_ascii=False)}

Berikan respons yang natural, empatis, dan membantu sesuai konteks.
- Jika PUSH_BACK: akui keberatan user, tawarkan alternatif atau klarifikasi.
- Jika CONFIRMATION: konfirmasi pemahaman dan tanyakan langkah selanjutnya.
- Jika CONSTRAINT_UPDATE: akui update constraint dan tanyakan apakah perlu revisi learning path.
{drift_note}

Respons dalam Bahasa Indonesia yang hangat dan tidak lebih dari 3 paragraf."""

    try:
        response_text = _call_llm(prompt)
    except Exception as e:
        response_text = (
            "Terima kasih sudah berbagi! Ada yang bisa aku bantu lebih lanjut? 😊"
        )

    return {
        **state,
        "agent_response": response_text,
    }