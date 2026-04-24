"""Middleware: upsert Client и Dialog, прокидывает их в хендлеры через data."""
from __future__ import annotations

from collections.abc import Awaitable, Callable
from typing import Any

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, Update, User

from app.common.logger import get_logger
from app.db.repositories.clients import get_or_create_dialog, upsert_from_tg
from app.db.session import session_scope

log = get_logger(__name__)


class ClientContextMiddleware(BaseMiddleware):
    """Привязывает Client и Dialog к каждому апдейту."""

    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        tg_user: User | None = data.get("event_from_user")
        if tg_user is None or tg_user.is_bot:
            return await handler(event, data)

        async with session_scope() as session:
            client, created = await upsert_from_tg(session, tg_user)
            dialog = await get_or_create_dialog(session, client.id)
            if created:
                log.info("client_created", tg_user_id=tg_user.id, client_id=client.id)

            data["client"] = client
            data["dialog"] = dialog
            data["session"] = session

            return await handler(event, data)
