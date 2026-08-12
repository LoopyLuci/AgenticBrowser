"""Telegram bot capability for AgenticBrowser."""
from __future__ import annotations

import asyncio
import logging
from dataclasses import dataclass, field
from typing import Any

logger = logging.getLogger(__name__)


class TelegramBotError(Exception):
    """Raised when the Telegram bot cannot start or handle an update."""


@dataclass
class TelegramUpdate:
    update_id: int
    chat_id: int
    text: str | None = None
    username: str | None = None


class TelegramBot:
    def __init__(self, token: str, allowed_chat_ids: list[str] | None = None):
        self.token = token
        self.allowed_chat_ids = {str(chat_id) for chat_id in (allowed_chat_ids or [])}
        self._running = False

    async def handle_update(self, update: TelegramUpdate) -> str:
        if self.allowed_chat_ids and str(update.chat_id) not in self.allowed_chat_ids:
            raise TelegramBotError("Forbidden chat")

        if not update.text:
            return "Empty message"

        text = update.text.strip()
        if text.startswith("/"):
            return await self.handle_command(update, text)
        return await self.handle_message(update, text)

    async def handle_command(self, update: TelegramUpdate, command: str) -> str:
        command = command.split()[0].lower()
        if command == "/start":
            return "AgenticBrowser Telegram bot is ready."
        if command == "/help":
            return "Send a message to chat, or /status for bot state."
        if command == "/status":
            return "OK"
        return f"Unknown command: {command}"

    async def handle_message(self, update: TelegramUpdate, text: str) -> str:
        return f"Echo: {text}"

    async def start(self) -> None:
        self._running = True
        logger.info("Telegram bot started")

    async def stop(self) -> None:
        self._running = False
        logger.info("Telegram bot stopped")
