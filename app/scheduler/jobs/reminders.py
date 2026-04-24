"""Напоминания о завтрашних занятиях и диагностиках."""
from __future__ import annotations

from app.common.logger import get_logger

log = get_logger(__name__)


async def remind_tomorrow() -> None:
    """Каждый вечер в 18:00 — собрать завтрашние занятия и ДИ,
    отправить родителям напоминание с кнопками «Буду / Не смогу / Опоздаю».

    TODO: запрос в БД + Bot API.
    """
    log.info("remind_tomorrow_tick")
