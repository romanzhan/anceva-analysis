"""Правила эскалации: решают, когда бот замолкает и зовёт человека."""
from __future__ import annotations

from app.domain.rules import (
    HARD_ESCALATION_KEYWORDS,
    SOFT_ESCALATION_KEYWORDS,
    needs_hard_escalation,
    needs_soft_escalation,
)


def trigger_hard_escalation(text: str) -> str | None:
    """Если надо — вернёт конкретный триггер (для логов), иначе None."""
    if not needs_hard_escalation(text):
        return None
    lo = text.lower()
    for kw in HARD_ESCALATION_KEYWORDS:
        if kw in lo:
            return f"hard:{kw}"
    return "hard:unknown"


def should_soft_escalate(text: str) -> str | None:
    if not needs_soft_escalation(text):
        return None
    lo = text.lower()
    for kw in SOFT_ESCALATION_KEYWORDS:
        if kw in lo:
            return f"soft:{kw}"
    return "soft:unknown"
