import pytest

from app.providers.telegram_bot import TelegramBot, TelegramUpdate, TelegramBotError


def test_telegram_bot_start_stop():
    bot = TelegramBot("token")
    assert not bot._running
    assert __import__("asyncio").run(bot.start()) is None
    assert bot._running
    assert __import__("asyncio").run(bot.stop()) is None
    assert not bot._running


def test_telegram_bot_handle_command_start():
    bot = TelegramBot("token")
    reply = __import__("asyncio").run(bot.handle_update(TelegramUpdate(1, 2, text="/start")))
    assert reply == "AgenticBrowser Telegram bot is ready."


def test_telegram_bot_handle_command_help():
    bot = TelegramBot("token")
    reply = __import__("asyncio").run(bot.handle_update(TelegramUpdate(1, 2, text="/help")))
    assert "Send a message" in reply


def test_telegram_bot_handle_command_status():
    bot = TelegramBot("token")
    reply = __import__("asyncio").run(bot.handle_update(TelegramUpdate(1, 2, text="/status")))
    assert reply == "OK"


def test_telegram_bot_handle_unknown_command():
    bot = TelegramBot("token")
    reply = __import__("asyncio").run(bot.handle_update(TelegramUpdate(1, 2, text="/unknown")))
    assert "Unknown command" in reply


def test_telegram_bot_echo_message():
    bot = TelegramBot("token")
    reply = __import__("asyncio").run(bot.handle_update(TelegramUpdate(1, 2, text="hello")))
    assert reply == "Echo: hello"


def test_telegram_bot_empty_message():
    bot = TelegramBot("token")
    reply = __import__("asyncio").run(bot.handle_update(TelegramUpdate(1, 2, text="")))
    assert reply == "Empty message"


def test_telegram_bot_blocks_forbidden_chat():
    bot = TelegramBot("token", allowed_chat_ids=["99"])
    with pytest.raises(TelegramBotError, match="Forbidden chat"):
        __import__("asyncio").run(bot.handle_update(TelegramUpdate(1, 2, text="hi")))
