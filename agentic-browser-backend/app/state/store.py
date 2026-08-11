import sqlite3
import json
import os
from typing import Optional, List, Dict, Any


DB_PATH = os.getenv("AGENTIC_STATE_DB", ".agentic-state.db")


def _conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def configure_db(db_path: str):
    global DB_PATH
    DB_PATH = db_path


def init_state_db():
    with _conn() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS sessions (
                session_id TEXT PRIMARY KEY,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT,
                role TEXT,
                content TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(session_id) REFERENCES sessions(session_id)
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS settings (
                key TEXT PRIMARY KEY,
                value TEXT,
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
            """
        )


def get_or_create_session(session_id: str):
    with _conn() as conn:
        cur = conn.execute("SELECT session_id FROM sessions WHERE session_id = ?", (session_id,))
        if not cur.fetchone():
            conn.execute("INSERT INTO sessions(session_id) VALUES(?)", (session_id,))
        return session_id


def append_message(session_id: str, role: str, content: str):
    with _conn() as conn:
        conn.execute(
            "INSERT INTO messages(session_id, role, content) VALUES(?, ?, ?)",
            (session_id, role, content),
        )
        conn.execute(
            "UPDATE sessions SET updated_at = CURRENT_TIMESTAMP WHERE session_id = ?",
            (session_id,),
        )


def get_messages(session_id: str, limit: int = 200):
    with _conn() as conn:
        cur = conn.execute(
            "SELECT role, content FROM messages WHERE session_id = ? ORDER BY id DESC LIMIT ?",
            (session_id, limit),
        )
        rows = cur.fetchall()
        return [{"role": r["role"], "content": r["content"]} for r in reversed(rows)]


def set_setting(key: str, value: str):
    with _conn() as conn:
        conn.execute(
            "INSERT INTO settings(key, value) VALUES(?, ?) ON CONFLICT(key) DO UPDATE SET value = excluded.value, updated_at = CURRENT_TIMESTAMP",
            (key, value),
        )


def get_setting(key: str) -> Optional[str]:
    with _conn() as conn:
        cur = conn.execute("SELECT value FROM settings WHERE key = ?", (key,))
        row = cur.fetchone()
        return row["value"] if row else None


def export_settings() -> Dict[str, Optional[str]]:
    with _conn() as conn:
        cur = conn.execute("SELECT key, value FROM settings")
        return {r["key"]: r["value"] for r in cur.fetchall()}


def import_settings(data: Dict[str, Optional[str]]):
    with _conn() as conn:
        for key, value in data.items():
            conn.execute(
                "INSERT INTO settings(key, value) VALUES(?, ?) ON CONFLICT(key) DO UPDATE SET value = excluded.value, updated_at = CURRENT_TIMESTAMP",
                (key, value),
            )
