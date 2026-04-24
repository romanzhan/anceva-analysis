"""Тесты прайсового модуля."""
from __future__ import annotations

from decimal import Decimal

from app.domain.enums import Direction
from app.domain.pricing import (
    INDIVIDUAL_TARIFFS,
    di_price,
    individual_monthly,
    kaspi_total,
)


def test_di_price_for_known_directions() -> None:
    assert di_price(Direction.DEFECTOLOGIST) == Decimal("12000")
    assert di_price(Direction.NEURO) == Decimal("15000")
    assert di_price(Direction.SCHOOL_PREP) == Decimal("10000")


def test_di_price_unknown_defaults() -> None:
    # На случай если ENUM вырастет — дефолтимся в 9000
    assert di_price(Direction.MASSAGE) == Decimal("0")


def test_individual_monthly_lookup() -> None:
    assert individual_monthly(30, 2) == Decimal("44000")
    assert individual_monthly(45, 3) == Decimal("88000")
    assert individual_monthly(60, 5) == Decimal("165000")
    assert individual_monthly(99, 99) is None


def test_kaspi_surcharge() -> None:
    assert kaspi_total(Decimal("44000")) == Decimal("46000")


def test_tariffs_sane() -> None:
    for t in INDIVIDUAL_TARIFFS:
        assert t.monthly_price > 0
        assert t.per_week in (2, 3, 5)
        assert t.duration_min in (30, 45, 60)
