import sqlite3
import json
from datetime import datetime

DB_PATH = "data/matcha.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS user_sessions (
            session_id TEXT PRIMARY KEY,
            profile_json TEXT,
            intent_history TEXT,
            updated_at TEXT
        )
    """)
    conn.commit()
    conn.close()

def save_session(session_id: str, state: dict):
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""
        INSERT OR REPLACE INTO user_sessions
        VALUES (?, ?, ?, ?)
    """, (
        session_id,
        json.dumps(state.get("user_profile"), ensure_ascii=False),
        json.dumps(state.get("previous_intent_history", []), ensure_ascii=False),
        datetime.now().isoformat()
    ))
    conn.commit()
    conn.close()

def load_session(session_id: str) -> dict:
    conn = sqlite3.connect(DB_PATH)
    row = conn.execute(
        "SELECT * FROM user_sessions WHERE session_id = ?",
        (session_id,)
    ).fetchone()
    conn.close()
    if not row:
        return {}
    return {
        "user_profile": json.loads(row[1]) if row[1] else None,
        "previous_intent_history": json.loads(row[2]) if row[2] else [],
    }