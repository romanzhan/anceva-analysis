"""Служебные команды: /admin, /menu, /schedule, /payment, /cancel, /help."""
from __future__ import annotations

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from sqlalchemy.ext.asyncio import AsyncSession

from app.bot.keyboards import active_client_reply
from app.common.logger import get_logger
from app.db.models.dialog import Dialog
from app.domain.enums import DialogMode

router = Router(name="commands")
log = get_logger(__name__)


@router.message(Command("admin"))
async def cmd_admin(message: Message, dialog: Dialog, session: AsyncSession) -> None:
    """Клиент просит живого человека."""
    dialog.mode = DialogMode.ADMIN
    await session.commit()
    await message.answer(
        "Конечно! Я сейчас передам Ваш вопрос администратору — ответит Вам лично 🌿"
    )
    # TODO: нотифицировать admin_bot


@router.message(Command("menu"))
async def cmd_menu(message: Message) -> None:
    await message.answer("Меню:", reply_markup=active_client_reply())


@router.message(Command("help"))
async def cmd_help(message: Message) -> None:
    await message.answer(
        "Короткая справка:\n\n"
        "— Напишите нам своими словами, я разберу запрос и подберу формат.\n"
        "— /menu — быстрые действия (для активных клиентов)\n"
        "— /admin — передать диалог живому администратору\n"
        "— /cancel — отменить текущее действие"
    )


@router.message(Command("cancel"))
async def cmd_cancel(message: Message) -> None:
    await message.answer("Хорошо, начнём сначала. Чем можем помочь?")


@router.message(Command("schedule"))
async def cmd_schedule(message: Message) -> None:
    # TODO: вывести расписание занятий клиента из БД
    await message.answer("Расписание появится здесь после первой диагностики 🌿")


@router.message(Command("payment"))
async def cmd_payment(message: Message) -> None:
    # TODO: выставленный счёт + история
    await message.answer("Текущих счетов нет. Если что-то появится — пришлём сюда.")
