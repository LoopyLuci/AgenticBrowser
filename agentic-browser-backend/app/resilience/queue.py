import sqlite3
import json
import os
from typing import Optional, Dict, Any

DB_PATH = os.getenv("AGENTIC_QUEUE_DB", ".agentic-queue.db")


def _conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    with _conn() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS jobs (
              id INTEGER PRIMARY KEY AUTOINCREMENT,
              provider TEXT,
              model TEXT,
              messages TEXT,
              created_at TEXT DEFAULT CURRENT_TIMESTAMP,
              attempts INTEGER DEFAULT 0,
              last_error TEXT
            )
            """
        )
        conn.commit()


def enqueue(provider: str, model: str, messages: list):
    with _conn() as conn:
        conn.execute(
            "INSERT INTO jobs(provider, model, messages) VALUES(?,?,?)",
            (provider, model, json.dumps(messages)),
        )
        conn.commit()


def next_job() -> Optional[Dict[str, Any]]:
    with _conn() as conn:
        row = conn.execute("SELECT id, provider, model, messages, attempts FROM jobs ORDER BY id ASC LIMIT 1").fetchone()
        if not row:
            return None
        return {
            "id": row["id"],
            "provider": row["provider"],
            "model": row["model"],
            "messages": json.loads(row["messages"]),
            "attempts": row["attempts"],
        }


def mark_done(job_id: int):
    with _conn() as conn:
        conn.execute("DELETE FROM jobs WHERE id = ?", (job_id,))
        conn.commit()


def mark_failed(job_id: int, error: str):
    with _conn() as conn:
        conn.execute("UPDATE jobs SET attempts = attempts + 1, last_error = ? WHERE id = ?", (error, job_id))
        conn.commit()
