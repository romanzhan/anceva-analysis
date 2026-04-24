"""Тесты доменных правил — возраст, эскалация, переносы."""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
from decimal import Decimal

import pytest

from app.domain.enums import AgeBand, Direction
from app.domain.rules import (
    classify_age,
    needs_hard_escalation,
    needs_soft_escalation,
    suggest_directions,
    verdict_for_di_cancellation,
)


@pytest.mark.parametrize(
    "years,months,expected",
    [
        (0, 8, AgeBand.INFANT),
        (1, 11, AgeBand.INFANT),
        (2, 0, AgeBand.TODDLER),
        (4, 11, AgeBand.TODDLER),
        (5, 0, AgeBand.PRESCHOOL),
        (5, 11, AgeBand.PRESCHOOL),
        (6, 0, AgeBand.PRE_SCHOOL),
        (7, 0, AgeBand.SCHOOL),
        (13, 11, AgeBand.SCHOOL),
        (14, 0, AgeBand.TEEN),
        (16, 5, AgeBand.TEEN),
    ],
)
def test_classify_age(years: int, months: int, expected: AgeBand) -> None:
    assert classify_age(years, months) is expected


def test_suggest_directions_has_sane_defaults() -> None:
    assert Direction.MOTHER_CHILD in suggest_directions(AgeBand.INFANT)
    assert Direction.SCHOOL_PREP in suggest_directions(AgeBand.PRE_SCHOOL)
    assert Direction.NEURO in suggest_directions(AgeBand.SCHOOL)


def test_hard_escalation_detects_keywords() -> None:
    assert needs_hard_escalation("Я подам жалобу")
    assert needs_hard_escalation("хочу Марию Сергеевну лично")
    assert not needs_hard_escalation("Добрый день, сыну 3 года")


def test_soft_escalation_on_emotion() -> None:
    assert needs_soft_escalation("Я уже не знаю куда бежать")
    assert not needs_soft_escalation("Просто интересуюсь ценой")


def test_di_cancel_first_transfer_is_free() -> None:
    now = datetime(2026, 5, 1, 12, 0, tzinfo=timezone.utc)
    di_at = now + timedelta(days=2)
    verdict = verdict_for_di_cancellation(
        di_at=di_at, now=now, di_price=Decimal("9000"), transfer_count=0
    )
    assert verdict.allowed
    assert not verdict.burns


def test_di_cancel_second_transfer_burns() -> None:
    now = datetime(2026, 5, 1, 12, 0, tzinfo=timezone.utc)
    di_at = now + timedelta(days=2)
    verdict = verdict_for_di_cancellation(
        di_at=di_at, now=now, di_price=Decimal("9000"), transfer_count=2
    )
    assert not verdict.allowed
    assert verdict.burns
