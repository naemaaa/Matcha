"""
memory.py — Session Persistence untuk Matcha
Menyimpan dan memuat state percakapan user menggunakan SQLite.
"""

import json
import os
import sqlite3
from typing import Optional, Dict, Any

DB_PATH = os.environ.get("MATCHA_DB_PATH", "matcha_sessions.db")


# ─────────────────────────────────────────────
# Init Database
# ─────────────────────────────────────────────

def init_db():
    """Buat tabel sessions jika belum ada."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS sessions (
            session_id TEXT PRIMARY KEY,
            state_json  TEXT NOT NULL,
            updated_at  DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()


# ─────────────────────────────────────────────
# Save Session
# ─────────────────────────────────────────────

def save_session(session_id: str, state: Dict[str, Any]):
    """
    Simpan state agent ke database.
    Hanya menyimpan field yang penting (bukan pesan chat — itu di session_state Streamlit).
    """
    fields_to_save = [
        "user_profile",
        "skill_gaps",
        "detected_intent",
        "previous_intent_history",
        "drift_detected",
        "cv_text",
        "linkedin_text",
        "job_description",
    ]
    payload = {k: state.get(k) for k in fields_to_save}

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO sessions (session_id, state_json, updated_at)
        VALUES (?, ?, CURRENT_TIMESTAMP)
        ON CONFLICT(session_id) DO UPDATE SET
            state_json = excluded.state_json,
            updated_at = CURRENT_TIMESTAMP
    """, (session_id, json.dumps(payload, ensure_ascii=False)))
    conn.commit()
    conn.close()


# ─────────────────────────────────────────────
# Load Session
# ─────────────────────────────────────────────

def load_session(session_id: str) -> Optional[Dict[str, Any]]:
    """
    Muat state agent dari database berdasarkan session_id.
    Kembalikan dict kosong jika session tidak ditemukan.
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "SELECT state_json FROM sessions WHERE session_id = ?",
        (session_id,)
    )
    row = cursor.fetchone()
    conn.close()

    if row:
        return json.loads(row[0])
    return {}