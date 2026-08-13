"""Telegram bot capability for AgenticBrowser."""
from __future__ import annotations

import asyncio
import json
import logging
import urllib.error
import urllib.request
from dataclasses import dataclass
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
        self._offset = 0
        self._task: asyncio.Task | None = None
        self._commands = [
            {"command": "start", "description": "Start the bot"},
            {"command": "help", "description": "Show help"},
            {"command": "status", "description": "Bot status"},
            {"command": "summon", "description": "Summon the agent in allowed chats"},
        ]

    async def _api(self, method: str, payload: dict[str, Any]) -> dict[str, Any]:
        url = f"https://api.telegram.org/bot{self.token}/{method}"
        data = json.dumps(payload).encode()
        req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"})
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                return json.loads(resp.read())
        except urllib.error.HTTPError as exc:
            raise TelegramBotError(f"Telegram API error: {exc.code} {exc.reason}") from exc
        except urllib.error.URLError as exc:
            raise TelegramBotError(f"Telegram network error: {exc.reason}") from exc

    async def _register_commands(self) -> None:
        await self._api("setMyCommands", {"commands": self._commands})

    async def _send(self, chat_id: str, text: str) -> dict[str, Any]:
        return await self._api("sendMessage", {"chat_id": chat_id, "text": text})

    async def _poll(self) -> None:
        params = {"timeout": 20}
        if self._offset:
            params["offset"] = self._offset
        result = await self._api("getUpdates", params)
        updates = result.get("result", [])
        for update in updates:
            self._offset = update["update_id"] + 1
            await self._process(update)

    async def _process(self, update: dict[str, Any]) -> None:
        message = update.get("message") or update.get("edited_message")
        if not message:
            return
        chat_id = str(message["chat"]["id"])
        text = message.get("text", "")
        username = message.get("from", {}).get("username")
        telegram_update = TelegramUpdate(
            update_id=update["update_id"],
            chat_id=int(chat_id),
            text=text,
            username=username,
        )
        try:
            if self.allowed_chat_ids and chat_id not in self.allowed_chat_ids:
                if text.startswith("/summon"):
                    await self._send(chat_id, "This chat is not allowed.")
                return
            reply = await self.handle_update(telegram_update)
            await self._send(chat_id, reply)
        except TelegramBotError as exc:
            logger.error("Telegram bot error: %s", exc)

    async def _run(self) -> None:
        logger.info("Telegram bot loop started")
        try:
            await self._register_commands()
        except TelegramBotError:
            logger.exception("Failed to register Telegram commands")
        while self._running:
            try:
                await asyncio.wait_for(self._poll(), timeout=25)
            except asyncio.TimeoutError:
                continue
            except TelegramBotError:
                logger.exception("Telegram poll error")
                await asyncio.sleep(1)

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
            return "Send a message to chat, /status for bot state, /summon in allowed chats."
        if command == "/status":
            return "OK"
        if command == "/summon":
            return "Agent summoned." if self.allowed_chat_ids else "No allowed chats configured."
        return f"Unknown command: {command}"

    async def handle_message(self, update: TelegramUpdate, text: str) -> str:
        return f"Echo: {text}"

    async def start(self) -> None:
        self._running = True
        self._task = asyncio.create_task(self._run())

    async def stop(self) -> None:
        self._running = False
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
            self._task = None
        logger.info("Telegram bot stopped")
