"""structlog-конфигурация.

Лог в stdout в одном из двух форматов:
- console — человекочитаемый (local / staging)
- json    — одна строка JSON на запись (production → подхватывается Railway / Sentry)
"""
from __future__ import annotations

import logging
import sys
from typing import Any

import structlog
from structlog.typing import Processor

from app.common.config import LogFormat, get_settings


def configure_logging() -> None:
    settings = get_settings()
    level = getattr(logging, settings.log_level.upper(), logging.INFO)

    shared_processors: list[Processor] = [
        structlog.contextvars.merge_contextvars,
        structlog.processors.add_log_level,
        structlog.processors.TimeStamper(fmt="iso", utc=True),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
    ]

    if settings.log_format is LogFormat.JSON:
        renderer: Processor = structlog.processors.JSONRenderer()
    else:
        renderer = structlog.dev.ConsoleRenderer(colors=True, pad_event=28)

    structlog.configure(
        processors=[*shared_processors, renderer],
        wrapper_class=structlog.make_filtering_bound_logger(level),
        context_class=dict,
        logger_factory=structlog.PrintLoggerFactory(file=sys.stdout),
        cache_logger_on_first_use=True,
    )

    # Соединяем stdlib logging (aiogram, sqlalchemy, uvicorn) с нашим рендерером
    logging.basicConfig(
        level=level,
        handlers=[_StructlogStdlibHandler()],
        format="%(message)s",
    )
    # Заглушим особо болтливых
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("aiogram.event").setLevel(logging.INFO)


class _StructlogStdlibHandler(logging.Handler):
    """Перенаправляет stdlib logging → structlog, сохраняя контекст."""

    def emit(self, record: logging.LogRecord) -> None:  # noqa: D401
        try:
            logger = structlog.get_logger(record.name)
            kw: dict[str, Any] = {}
            if record.exc_info:
                kw["exc_info"] = record.exc_info
            log = logger.bind(logger=record.name)
            getattr(log, record.levelname.lower(), log.info)(record.getMessage(), **kw)
        except Exception:  # noqa: BLE001 — хендлер не должен падать
            self.handleError(record)


def get_logger(name: str | None = None) -> structlog.stdlib.BoundLogger:
    """Короткая обёртка для модульного логгера."""
    return structlog.get_logger(name)
