"""
state.py — LangGraph State Definition untuk Matcha
Mendefinisikan struktur data yang mengalir antar node di graph.
"""

from typing import TypedDict, Optional, List, Dict, Any


class UserProfile(TypedDict, total=False):
    current_role: Optional[str]
    target_role: Optional[str]
    current_skills: List[str]
    hours_per_week: Optional[float]
    budget_idr: Optional[int]
    timeline_months: Optional[int]


class MatchaState(TypedDict, total=False):
    # === INPUT ===
    user_input: str                          # Pesan terbaru dari user
    messages: List[Dict[str, str]]           # Full chat history [{role, content}]

    # === DOKUMEN UPLOAD ===
    cv_text: Optional[str]                   # Teks hasil ekstraksi CV
    linkedin_text: Optional[str]             # Teks hasil ekstraksi LinkedIn PDF
    job_description: Optional[str]           # Job description yang di-paste user

    # === HASIL INTENT CLASSIFIER ===
    detected_intent: Optional[str]           # e.g. "CAREER_EXPLORATION"
    intent_confidence: Optional[float]       # 0.0 - 1.0
    extracted_info: Optional[Dict[str, Any]] # Info tambahan dari intent classifier

    # === PROFIL USER ===
    user_profile: Optional[UserProfile]      # Profil karir terstruktur

    # === SKILL GAP & LEARNING PATH ===
    skill_gaps: Optional[str]               # Output teks skill gap + learning path

    # === DRIFT DETECTION ===
    drift_detected: bool                     # True jika intent drift terdeteksi
    previous_intent_history: List[str]       # Riwayat intent untuk deteksi drift

    # === OUTPUT AGENT ===
    agent_response: Optional[str]            # Respons akhir yang ditampilkan ke user