"""Callback-кнопки (inline).

Обрабатывают нажатия на кнопки, генерируемые ботом во время диалога.
Пока — каркас, детали ветвей (slot, pay, lesson) заполняются по мере реализации
модулей расписания и оплат.
"""
from __future__ import annotations

from aiogram import F, Router
from aiogram.types import CallbackQuery

from app.common.logger import get_logger

router = Router(name="callbacks")
log = get_logger(__name__)


@router.callback_query(F.data.startswith("slot:"))
async def cb_slot_pick(callback: CallbackQuery) -> None:
    await callback.answer("Минуту, записываю…")
    # TODO: разбор слота + создание Diagnostic, переход на invoicing
    log.info("slot_picked", data=callback.data)


@router.callback_query(F.data == "pay:send_check")
async def cb_pay_send_check(callback: CallbackQuery) -> None:
    await callback.answer()
    await callback.message.answer(
        "Когда оплата пройдёт, просто пришлите сюда фото чека из Kaspi — мы закрепим бронь 🌿"
    )


@router.callback_query(F.data.startswith("lesson:"))
async def cb_lesson_action(callback: CallbackQuery) -> None:
    await callback.answer()
    action = callback.data.split(":", 1)[1] if callback.data else ""
    # TODO: отразить в БД (Lesson.notified_at / status), уведомить админа
    log.info("lesson_action", action=action)
    await callback.message.answer("Спасибо, учли! 🌿")
