"""Базовый rate-limit на пользователя — чтобы мусорные сообщения не ложили LLM."""
from __future__ import annotations

import time
from collections import defaultdict
from collections.abc import Awaitable, Callable
from typing import Any

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, User


class ThrottleMiddleware(BaseMiddleware):
    """Не больше N сообщений в секунду от одного пользователя."""

    def __init__(self, rate: float = 2.0) -> None:
        self.min_interval = 1.0 / rate
        self._last: dict[int, float] = defaultdict(float)

    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        tg_user: User | None = data.get("event_from_user")
        if tg_user is None or tg_user.is_bot:
            return await handler(event, data)

        now = time.monotonic()
        if now - self._last[tg_user.id] < self.min_interval:
            # молча игнорируем — пользователь просто увидит отсутствие ответа
            return None
        self._last[tg_user.id] = now
        return await handler(event, data)
