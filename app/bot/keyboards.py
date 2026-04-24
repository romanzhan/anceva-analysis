"""Клавиатуры и инлайн-кнопки."""
from __future__ import annotations

from datetime import datetime

from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardMarkup,
)

from app.common.clock import to_local


# ----------------------------- START -----------------------------------------

def start_inline() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Я родитель", callback_data="role:parent")],
            [InlineKeyboardButton(text="Я пишу о себе (14–16 лет)", callback_data="role:teen")],
        ]
    )


# ----------------------------- SLOTS -----------------------------------------

def slots_inline(slots: list[datetime]) -> InlineKeyboardMarkup:
    rows: list[list[InlineKeyboardButton]] = []
    for slot in slots[:3]:
        local = to_local(slot)
        label = local.strftime("%a, %d.%m · %H:%M")
        rows.append(
            [InlineKeyboardButton(text=label, callback_data=f"slot:{local.isoformat()}")]
        )
    rows.append(
        [InlineKeyboardButton(text="Другие даты", callback_data="slot:more")]
    )
    return InlineKeyboardMarkup(inline_keyboard=rows)


# ----------------------------- PAYMENT ---------------------------------------

def payment_inline(kaspi_url: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🔗 Перейти к оплате", url=kaspi_url)],
            [InlineKeyboardButton(text="Прислать чек", callback_data="pay:send_check")],
        ]
    )


# ----------------------------- REMINDER --------------------------------------

def lesson_reminder_inline() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="Буду", callback_data="lesson:confirm"),
                InlineKeyboardButton(text="Не смогу", callback_data="lesson:cancel"),
            ],
            [InlineKeyboardButton(text="Опоздаю", callback_data="lesson:late")],
        ]
    )


# ----------------------------- ACTIVE CLIENT MENU ----------------------------

def active_client_reply() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📅 Расписание"), KeyboardButton(text="💳 Оплаты")],
            [KeyboardButton(text="📝 Перенести"), KeyboardButton(text="❓ Вопрос")],
            [KeyboardButton(text="👤 Позвать администратора")],
        ],
        resize_keyboard=True,
    )


# ----------------------------- ANKETA ----------------------------------------

def anketa_inline(url: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Открыть анкету", url=url)]
        ]
    )
