"""Сезонные триггеры: ДР, 8 марта, Наурыз, 1 сент, НГ, Рождество."""
from __future__ import annotations

from datetime import date

from app.common.clock import now_local
from app.common.logger import get_logger

log = get_logger(__name__)


SEASONAL_DATES: dict[tuple[int, int], str] = {
    (3, 8): "8_march",
    (3, 22): "nauryz",
    (9, 1): "school_start",
    (12, 31): "new_year_eve",
    (1, 7): "christmas",
}


async def send_daily_triggers() -> None:
    """Ежедневно в 9:00 проверяем:
       - День рождения ребёнка у активных клиентов.
       - Сезонная дата.
    Формируем черновики рассылок / индивидуальные поздравления.

    TODO: сам запуск рассылки — из веб-админки (с одобрения админа).
    """
    today = now_local().date()
    if _is_seasonal(today):
        log.info("seasonal_today", kind=SEASONAL_DATES[(today.month, today.day)])

    # TODO: найти детей с ДР сегодня и создать задачи
    log.info("seasonal_check_done", date=today.isoformat())


def _is_seasonal(d: date) -> bool:
    return (d.month, d.day) in SEASONAL_DATES
