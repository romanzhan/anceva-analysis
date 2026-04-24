"""Работа со временем — всегда через эти функции.

Причина: удобно мокать в тестах (freezegun) + никогда не использовать naive datetime.
"""
from __future__ import annotations

from datetime import UTC, datetime
from zoneinfo import ZoneInfo

from app.common.config import get_settings


def now_utc() -> datetime:
    """Текущее время UTC, tz-aware."""
    return datetime.now(UTC)


def now_local() -> datetime:
    """Текущее время в таймзоне центра (Караганда)."""
    return datetime.now(ZoneInfo(get_settings().tz))


def to_local(dt: datetime) -> datetime:
    """Перевод tz-aware datetime в локальную таймзону центра."""
    if dt.tzinfo is None:
        raise ValueError("naive datetime не принимается — задай tz явно")
    return dt.astimezone(ZoneInfo(get_settings().tz))
