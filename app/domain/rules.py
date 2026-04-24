"""Бизнес-правила центра.

Основано на чек-листе «Оплата и правила» и подтверждено чатами за 2024–2026.
Все правила — pure функции без side-effects, легко тестируются.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, time
from decimal import Decimal

from app.common.clock import to_local
from app.domain.enums import AgeBand, Direction


# -------------------- ВОЗРАСТ → ВЕТКА ----------------------------------------

def classify_age(years: int, months: int = 0) -> AgeBand:
    """Определяет возрастную ветку по возрасту в годах и месяцах."""
    total_months = years * 12 + months
    if total_months < 24:
        return AgeBand.INFANT
    if total_months < 60:
        return AgeBand.TODDLER
    if total_months < 72:
        # 5–6 лет — пересекающаяся зона, по умолчанию идём в PRESCHOOL.
        # Если у ребёнка запрос на школу — перейдём в PRE_SCHOOL уточняющим вопросом.
        return AgeBand.PRESCHOOL
    if total_months < 84:
        return AgeBand.PRE_SCHOOL
    if total_months < 168:  # до 14 лет
        return AgeBand.SCHOOL
    return AgeBand.TEEN


def suggest_directions(age: AgeBand) -> list[Direction]:
    """Какие направления в первую очередь рассматриваем для этой ветки."""
    match age:
        case AgeBand.INFANT:
            return [Direction.MOTHER_CHILD, Direction.SPEECH_LAUNCH]
        case AgeBand.TODDLER:
            return [Direction.SPEECH_LAUNCH, Direction.DEFECTOLOGIST, Direction.AFK]
        case AgeBand.PRESCHOOL:
            return [Direction.ARTICULATION, Direction.DEFECTOLOGIST, Direction.GROUP_CORRECTIONAL]
        case AgeBand.PRE_SCHOOL:
            return [Direction.SCHOOL_PREP, Direction.ARTICULATION, Direction.GROUP_CORRECTIONAL]
        case AgeBand.SCHOOL:
            return [Direction.ARTICULATION, Direction.NEURO, Direction.STUTTERING]
        case AgeBand.TEEN:
            return [Direction.ARTICULATION]


# -------------------- ПРАВИЛА ПЕРЕНОСА ЗАНЯТИЙ -------------------------------

NOTIFY_CUTOFF = time(hour=19, minute=0)  # до 19:00 предыдущего дня


@dataclass(frozen=True, slots=True)
class CancellationVerdict:
    allowed: bool              # можно ли перенести/отработать
    refund: Decimal            # сколько возвращаем денег (для ДИ)
    burns: bool                # сгорает ли бронь (для ДИ)
    reason: str                # человеко-читаемое объяснение


def verdict_for_lesson_cancellation(
    *,
    lesson_at: datetime,
    notified_at: datetime,
) -> CancellationVerdict:
    """Правило для пропуска обычного занятия.

    - Предупредил до 19:00 предыдущего дня → перерасчёт в текущем месяце.
    - Предупредил позже (день-в-день) → занятие считается проведённым.
    """
    lesson_local = to_local(lesson_at)
    notified_local = to_local(notified_at)
    cutoff = datetime.combine(lesson_local.date(), NOTIFY_CUTOFF).replace(
        tzinfo=lesson_local.tzinfo
    )
    cutoff = cutoff.replace(day=cutoff.day - 1)

    if notified_local <= cutoff:
        return CancellationVerdict(
            allowed=True,
            refund=Decimal("0"),
            burns=False,
            reason="предупреждение до 19:00 предыдущего дня — отработка в текущем месяце",
        )
    return CancellationVerdict(
        allowed=False,
        refund=Decimal("0"),
        burns=False,
        reason="предупреждение день-в-день — занятие считается проведённым",
    )


def verdict_for_di_cancellation(
    *,
    di_at: datetime,
    now: datetime,
    di_price: Decimal,
    transfer_count: int,
) -> CancellationVerdict:
    """Правило для переноса / отмены диагностики.

    - Первый перенос — бесплатно.
    - Второй — бронь сгорает, оплата заново.
    - Отмена > 24 часов — 50% возврата.
    - Отмена ≤ 24 часов — оплата не возвращается.
    """
    di_local = to_local(di_at)
    now_local = to_local(now)
    hours_until = (di_local - now_local).total_seconds() / 3600

    if transfer_count == 0:
        return CancellationVerdict(
            allowed=True,
            refund=Decimal("0"),
            burns=False,
            reason="первый перенос — бесплатно",
        )
    if transfer_count >= 2:
        return CancellationVerdict(
            allowed=False,
            refund=Decimal("0"),
            burns=True,
            reason="второй перенос — бронь сгорает, требуется повторная оплата",
        )

    # Полная отмена (не перенос)
    if hours_until > 24:
        return CancellationVerdict(
            allowed=True,
            refund=di_price * Decimal("0.5"),
            burns=True,
            reason="отмена более чем за 24 часа — возврат 50%",
        )
    return CancellationVerdict(
        allowed=False,
        refund=Decimal("0"),
        burns=True,
        reason="отмена менее чем за 24 часа — оплата не возвращается",
    )


# -------------------- ЭСКАЛАЦИЯ ---------------------------------------------

# Слова-триггеры, которые однозначно эскалируют диалог человеку.
HARD_ESCALATION_KEYWORDS: frozenset[str] = frozenset(
    {
        "жалоба",
        "жалуюсь",
        "вернуть деньги",
        "возврат",
        "суд",
        "роспотребнадзор",
        "прокуратура",
        "отказаться",
        "отказываюсь",
        "хочу поговорить с",
        "с человеком",
        "живого человека",
        "марию сергеевну лично",
    }
)

# Слова-сигналы эмоционального кризиса.
SOFT_ESCALATION_KEYWORDS: frozenset[str] = frozenset(
    {
        "не знаю куда бежать",
        "куда бежать",
        "уже не знаю",
        "отчаиваюсь",
        "плачу",
        "очень переживаю",
        "мне страшно",
    }
)


def needs_hard_escalation(text: str) -> bool:
    """True если в сообщении есть слова, которые точно требуют человека."""
    lo = text.lower()
    return any(kw in lo for kw in HARD_ESCALATION_KEYWORDS)


def needs_soft_escalation(text: str) -> bool:
    """True если сообщение эмоционально тяжёлое — бот пишет заглушку, админ решает дальше."""
    lo = text.lower()
    return any(kw in lo for kw in SOFT_ESCALATION_KEYWORDS)
