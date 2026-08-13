import os
from pathlib import Path

import pytest

from app.settings.store import SettingsStore, SETTINGS_DB_PATH


def test_settings_store_persists_values(tmp_path):
    db_path = str(tmp_path / "settings.db")
    os.environ["SETTINGS_DB_PATH"] = db_path
    try:
        store = SettingsStore()
        store.set("ollama_host", "http://localhost:11434")
        store.set("openrouter_key", "sk-123")

        assert store.get("ollama_host") == "http://localhost:11434"
        assert store.get("openrouter_key") == "sk-123"
        assert store.get("missing", "default") == "default"
    finally:
        os.environ.pop("SETTINGS_DB_PATH", None)


def test_settings_store_to_dict_roundtrip(tmp_path):
    db_path = str(tmp_path / "settings.db")
    os.environ["SETTINGS_DB_PATH"] = db_path
    try:
        store = SettingsStore()
        store.set("provider", "ollama")
        store.set("telegram_allowed_chat_ids", [1, 2, 3])
        result = store.to_dict()
        assert result["provider"] == "ollama"
        assert result["telegram_allowed_chat_ids"] == [1, 2, 3]
    finally:
        os.environ.pop("SETTINGS_DB_PATH", None)
