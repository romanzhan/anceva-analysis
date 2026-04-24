"""Админ-пульт в Telegram. Уведомления, handoff, быстрые команды.

Запуск: python -m app.admin_bot.main
Всегда long polling (нет смысла держать отдельный webhook).
"""
from __future__ import annotations

import asyncio

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from app.admin_bot.handlers import commands, handoff, notifications
from app.common.config import get_settings
from app.common.logger import configure_logging, get_logger

log = get_logger("admin_bot")


def build_dispatcher() -> Dispatcher:
    dp = Dispatcher()
    dp.include_router(commands.router)
    dp.include_router(notifications.router)
    dp.include_router(handoff.router)
    return dp


async def run() -> None:
    configure_logging()
    settings = get_settings()

    token = settings.bot_token_admin.get_secret_value()
    if not token:
        raise SystemExit("BOT_TOKEN_ADMIN не задан")

    bot = Bot(
        token=token,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )
    dp = build_dispatcher()

    me = await bot.get_me()
    log.info("admin_bot_started", username=me.username)

    try:
        await dp.start_polling(bot, handle_signals=True)
    finally:
        await bot.session.close()


def main() -> None:
    asyncio.run(run())


if __name__ == "__main__":
    main()
