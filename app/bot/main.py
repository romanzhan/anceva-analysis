"""Клиентский Telegram-бот. Точка входа.

Запуск:  python -m app.bot.main
Режим: webhook (если задан BOT_WEBHOOK_URL) или long polling (локально).
"""
from __future__ import annotations

import asyncio

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
from aiohttp import web

from app.bot.handlers import callbacks, commands, dialog, media, payment, start
from app.bot.middlewares.client_ctx import ClientContextMiddleware
from app.bot.middlewares.throttle import ThrottleMiddleware
from app.common.config import get_settings
from app.common.logger import configure_logging, get_logger

log = get_logger("bot")


def build_dispatcher() -> Dispatcher:
    dp = Dispatcher()

    # Middlewares — порядок важен
    dp.update.middleware(ThrottleMiddleware())
    dp.update.middleware(ClientContextMiddleware())

    # Handlers
    dp.include_router(start.router)
    dp.include_router(commands.router)
    dp.include_router(callbacks.router)
    dp.include_router(payment.router)
    dp.include_router(media.router)
    dp.include_router(dialog.router)  # catch-all текст — последним

    return dp


async def _on_startup(bot: Bot) -> None:
    me = await bot.get_me()
    log.info("bot_started", username=me.username, id=me.id)

    settings = get_settings()
    if settings.is_webhook_mode:
        await bot.set_webhook(
            url=settings.bot_webhook_url,
            secret_token=settings.bot_webhook_secret.get_secret_value() or None,
            drop_pending_updates=True,
        )
        log.info("webhook_set", url=settings.bot_webhook_url)


async def _on_shutdown(bot: Bot) -> None:
    settings = get_settings()
    if settings.is_webhook_mode:
        await bot.delete_webhook()
    await bot.session.close()
    log.info("bot_stopped")


async def run() -> None:
    configure_logging()
    settings = get_settings()

    token = settings.bot_token_client.get_secret_value()
    if not token:
        raise SystemExit("BOT_TOKEN_CLIENT не задан в окружении")

    bot = Bot(
        token=token,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )
    dp = build_dispatcher()

    if settings.is_webhook_mode:
        await _run_webhook(bot, dp)
    else:
        await _run_polling(bot, dp)


async def _run_polling(bot: Bot, dp: Dispatcher) -> None:
    await _on_startup(bot)
    try:
        await dp.start_polling(bot, handle_signals=True)
    finally:
        await _on_shutdown(bot)


async def _run_webhook(bot: Bot, dp: Dispatcher) -> None:
    settings = get_settings()

    app = web.Application()
    SimpleRequestHandler(
        dispatcher=dp,
        bot=bot,
        secret_token=settings.bot_webhook_secret.get_secret_value() or None,
    ).register(app, path="/webhook")

    setup_application(app, dp, bot=bot)

    # Health-check для Railway
    async def healthz(_: web.Request) -> web.Response:
        return web.Response(text="ok")
    app.router.add_get("/healthz", healthz)

    await _on_startup(bot)

    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, host=settings.web_host, port=settings.web_port)
    await site.start()
    log.info("webhook_listening", host=settings.web_host, port=settings.web_port)

    # держим процесс
    try:
        await asyncio.Event().wait()
    finally:
        await _on_shutdown(bot)
        await runner.cleanup()


def main() -> None:
    asyncio.run(run())


if __name__ == "__main__":
    main()
