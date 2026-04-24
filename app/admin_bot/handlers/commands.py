"""Команды админ-пульта: /today /tomorrow /inbox /escalations /unpaid /stats."""
from __future__ import annotations

from aiogram import Router
from aiogram.filters import Command, CommandStart
from aiogram.types import Message

router = Router(name="admin_commands")


@router.message(CommandStart())
async def cmd_start(message: Message) -> None:
    await message.answer(
        "Пульт администратора 🔧\n\n"
        "Команды:\n"
        "/today — занятия и диагностики сегодня\n"
        "/tomorrow — на завтра\n"
        "/inbox — диалоги, требующие ответа\n"
        "/escalations — активные эскалации\n"
        "/unpaid — просроченные оплаты\n"
        "/stats — короткая сводка"
    )


@router.message(Command("today"))
async def cmd_today(message: Message) -> None:
    # TODO: запросить из БД занятия и ДИ на сегодня
    await message.answer("На сегодня пока ничего не назначено.")


@router.message(Command("tomorrow"))
async def cmd_tomorrow(message: Message) -> None:
    await message.answer("На завтра пока ничего не назначено.")


@router.message(Command("inbox"))
async def cmd_inbox(message: Message) -> None:
    # TODO: список диалогов без ответа > 1ч, отсортированных по давности
    await message.answer("Inbox пустой 🌿")


@router.message(Command("escalations"))
async def cmd_escalations(message: Message) -> None:
    # TODO: диалоги с mode=admin, которые ещё никто не взял
    await message.answer("Активных эскалаций нет.")


@router.message(Command("unpaid"))
async def cmd_unpaid(message: Message) -> None:
    await message.answer("Просроченных оплат нет.")


@router.message(Command("stats"))
async def cmd_stats(message: Message) -> None:
    await message.answer(
        "📊 Сегодня:\n"
        "  Новые заявки: 0\n"
        "  Диалоги в работе: 0\n"
        "  Оплаты получены: 0 ₸"
    )
