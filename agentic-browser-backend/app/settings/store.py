import json
import os
import sqlite3
from pathlib import Path
from threading import Lock
from typing import Any, Dict, Optional

SETTINGS_DB_PATH = os.getenv("SETTINGS_DB_PATH", str(Path(__file__).resolve().parents[2] / "data" / "settings.db"))
_SETTINGS_LOCK = Lock()


def _ensure_db(db_path: str) -> sqlite3.Connection:
    Path(db_path).parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(db_path, check_same_thread=False)
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS settings (
            key TEXT PRIMARY KEY,
            value TEXT NOT NULL
        )
        """
    )
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS timeout_settings (
            key TEXT PRIMARY KEY,
            seconds INTEGER NOT NULL
        )
        """
    )
    conn.commit()
    return conn


class SettingsStore:
    def __init__(self, db_path: Optional[str] = None) -> None:
        self._db_path = db_path or SETTINGS_DB_PATH
        self._conn = _ensure_db(self._db_path)
        self._lock = Lock()

    def __getattr__(self, item: str) -> Any:
        try:
            return self.get(item)
        except AttributeError:
            raise AttributeError(f"SettingsStore object has no attribute '{item}'")

    def get(self, key: str, default: Any = None) -> Any:
        row = self._conn.execute("SELECT value FROM settings WHERE key = ?", (key,)).fetchone()
        if not row:
            return default
        value = row[0]
        try:
            return json.loads(value)
        except Exception:
            return value

    def set(self, key: str, value: Any) -> None:
        payload = json.dumps(value)
        with self._lock:
            self._conn.execute(
                "INSERT INTO settings(key, value) VALUES(?, ?) ON CONFLICT(key) DO UPDATE SET value = excluded.value",
                (key, payload),
            )
            self._conn.commit()

    def to_dict(self) -> Dict[str, Any]:
        rows = self._conn.execute("SELECT key, value FROM settings").fetchall()
        out: Dict[str, Any] = {}
        for key, value in rows:
            try:
                out[key] = json.loads(value)
            except Exception:
                out[key] = value
        timeout_rows = self._conn.execute("SELECT key, seconds FROM timeout_settings").fetchall()
        for key, seconds in timeout_rows:
            out[f"{key}Timeout"] = int(seconds)
        return out

    def get_timeout(self, key: str, default: int = 120) -> int:
        row = self._conn.execute("SELECT seconds FROM timeout_settings WHERE key = ?", (key,)).fetchone()
        if not row:
            return default
        return int(row[0])

    def set_timeout(self, key: str, seconds: int) -> None:
        with self._lock:
            self._conn.execute(
                "INSERT INTO timeout_settings(key, seconds) VALUES(?, ?) ON CONFLICT(key) DO UPDATE SET seconds = excluded.seconds",
                (key, int(seconds)),
            )
            self._conn.commit()
