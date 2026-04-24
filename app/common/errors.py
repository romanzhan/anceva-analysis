"""Иерархия исключений проекта.

Любое падение в бизнес-логике должно быть одним из этих классов.
Необработанные исключения логируются Sentry и приводят к эскалации диалога.
"""
from __future__ import annotations


class AncevaError(Exception):
    """Корневое исключение проекта."""


class ConfigError(AncevaError):
    """Ошибки конфигурации: отсутствуют обязательные переменные, кривой URL БД и т.п."""


class DomainError(AncevaError):
    """Нарушение бизнес-правила (некорректная цена, попытка третьего переноса и т.д.)."""


class LLMError(AncevaError):
    """Проблемы на уровне LLM-провайдера."""


class LLMTimeoutError(LLMError):
    """Таймаут обращения к Gemini."""


class LLMBadResponseError(LLMError):
    """LLM вернула ответ, не соответствующий ожидаемой схеме."""


class LLMContentFilterError(LLMError):
    """Ответ заблокирован safety-фильтрами провайдера."""


class DialogEscalateError(AncevaError):
    """Специальное исключение — сигнал, что диалог должен быть передан человеку."""

    def __init__(self, reason: str, *, soft: bool = False) -> None:
        super().__init__(reason)
        self.reason = reason
        self.soft = soft


class IntegrationError(AncevaError):
    """Ошибки внешних интеграций (Kaspi, Calendar, Telegram API выше 5xx)."""
