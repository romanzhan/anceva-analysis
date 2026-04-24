"""Генерация месячных счетов — 1 числа в 10:00."""
from __future__ import annotations

from app.common.logger import get_logger

log = get_logger(__name__)


async def generate_monthly() -> None:
    """Прокатиться по всем активным детям, посчитать количество занятий за предыдущий месяц
    по текущему тарифу, сформировать черновики Payment (status=draft).

    Отправку — по кнопке админа из веб-админки.

    TODO: реализовать расчёт и создание записей.
    """
    log.info("monthly_invoices_tick")
