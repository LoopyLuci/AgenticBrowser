import asyncio
from unittest.mock import AsyncMock, patch

import pytest

from app.providers.telegram_bot import TelegramBot, TelegramUpdate, TelegramBotError


@pytest.mark.asyncio
async def test_telegram_bot_start_stop():
    bot = TelegramBot("token")
    assert not bot._running
    with patch.object(bot, "_run", new_callable=AsyncMock):
        await bot.start()
    assert bot._running
    await bot.stop()
    assert not bot._running


@pytest.mark.asyncio
async def test_telegram_bot_handle_command_start():
    bot = TelegramBot("token")
    reply = await bot.handle_update(TelegramUpdate(1, 2, text="/start"))
    assert reply == "AgenticBrowser Telegram bot is ready."


@pytest.mark.asyncio
async def test_telegram_bot_handle_command_help():
    bot = TelegramBot("token")
    reply = await bot.handle_update(TelegramUpdate(1, 2, text="/help"))
    assert "Send a message" in reply


@pytest.mark.asyncio
async def test_telegram_bot_handle_command_status():
    bot = TelegramBot("token")
    reply = await bot.handle_update(TelegramUpdate(1, 2, text="/status"))
    assert reply == "OK"


@pytest.mark.asyncio
async def test_telegram_bot_handle_unknown_command():
    bot = TelegramBot("token")
    reply = await bot.handle_update(TelegramUpdate(1, 2, text="/unknown"))
    assert "Unknown command" in reply


@pytest.mark.asyncio
async def test_telegram_bot_echo_message():
    bot = TelegramBot("token")
    reply = await bot.handle_update(TelegramUpdate(1, 2, text="hello"))
    assert reply == "Echo: hello"


@pytest.mark.asyncio
async def test_telegram_bot_empty_message():
    bot = TelegramBot("token")
    reply = await bot.handle_update(TelegramUpdate(1, 2, text=""))
    assert reply == "Empty message"


@pytest.mark.asyncio
async def test_telegram_bot_blocks_forbidden_chat():
    bot = TelegramBot("token", allowed_chat_ids=["99"])
    with pytest.raises(TelegramBotError, match="Forbidden chat"):
        await bot.handle_update(TelegramUpdate(1, 2, text="hi"))
