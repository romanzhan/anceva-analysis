"""Прайс центра — источник истины.

В MVP читаем отсюда (хардкод). В фазе 2 переезжает в таблицу `price_tiers` с версионностью.

Цены актуальны на апрель 2026 (из чек-листа «Оплата и правила», тариф «НОВЫЕ»).
"""
from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal

from app.domain.enums import Direction


# -------------------------- ДИАГНОСТИКИ (ДИ) ---------------------------------

DI_PRICES: dict[Direction, Decimal] = {
    Direction.DEFECTOLOGIST: Decimal("12000"),
    Direction.ARTICULATION: Decimal("9000"),
    Direction.SCHOOL_PREP: Decimal("10000"),
    Direction.NEURO: Decimal("15000"),
    Direction.STUTTERING: Decimal("9000"),
    Direction.AFK: Decimal("10000"),
    Direction.SPEECH_LAUNCH: Decimal("9000"),
    Direction.MOTHER_CHILD: Decimal("9000"),
    Direction.GROUP_CORRECTIONAL: Decimal("9000"),
    Direction.MASSAGE: Decimal("0"),  # массаж без отдельной ДИ
}

DI_COMBO_DEFECTOLOGIST_AFK = Decimal("16000")
DI_COMBO_DEFECTOLOGIST_SCHOOL = Decimal("12000")


# -------------------------- ИНДИВИДУАЛЬНЫЕ ЗАНЯТИЯ ---------------------------

@dataclass(frozen=True, slots=True)
class IndividualTier:
    duration_min: int       # 30 / 45 / 60
    per_week: int           # 2 / 3 / 5
    monthly_price: Decimal
    est_lessons: int        # ожидаемое количество занятий в месяц


INDIVIDUAL_TARIFFS: tuple[IndividualTier, ...] = (
    # 30 мин
    IndividualTier(30, 2, Decimal("44000"), 9),
    IndividualTier(30, 3, Decimal("64000"), 13),
    IndividualTier(30, 5, Decimal("104000"), 22),
    # 45 мин
    IndividualTier(45, 2, Decimal("60000"), 9),
    IndividualTier(45, 3, Decimal("88000"), 13),
    IndividualTier(45, 5, Decimal("145000"), 22),
    # 60 мин
    IndividualTier(60, 2, Decimal("69000"), 9),
    IndividualTier(60, 3, Decimal("101000"), 13),
    IndividualTier(60, 5, Decimal("165000"), 22),
)


# -------------------------- ГРУППЫ -------------------------------------------

GROUP_MONTHLY: dict[str, Decimal] = {
    "mini_correctional_3w": Decimal("42000"),  # 3×/нед, 12-13 занятий
    "school_prep_3w_2h": Decimal("48000"),     # ПШ 3×/нед по 2ч
    "school_prep_5w_2h": Decimal("61000"),     # ПШ 5×/нед по 2ч
    "school_prep_5w_half": Decimal("75000"),   # ПШ 5×/нед полдня
    "mother_child": Decimal("27000"),          # М+М 8 занятий/мес
}

# Разовый взнос на канцелярию для ПШ (раз в учебный год)
SCHOOL_PREP_CANCELARY_YEARLY = Decimal("25000")


# -------------------------- МАССАЖ -------------------------------------------

MASSAGE_PER_SESSION = Decimal("8000")  # 45 мин, курс 8-12 сеансов


# -------------------------- КАСПИ --------------------------------------------

KASPI_SURCHARGE = Decimal("2000")  # надбавка за оплату через Каспи


# -------------------------- ФУНКЦИИ РАСЧЁТА ----------------------------------

def di_price(direction: Direction) -> Decimal:
    """Цена первичной диагностики по направлению."""
    return DI_PRICES.get(direction, Decimal("9000"))


def individual_monthly(duration_min: int, per_week: int) -> Decimal | None:
    """Месячная стоимость индивидуальных занятий для данного тарифа."""
    for tier in INDIVIDUAL_TARIFFS:
        if tier.duration_min == duration_min and tier.per_week == per_week:
            return tier.monthly_price
    return None


def kaspi_total(amount: Decimal) -> Decimal:
    """Итоговая сумма с учётом надбавки Kaspi."""
    return amount + KASPI_SURCHARGE
