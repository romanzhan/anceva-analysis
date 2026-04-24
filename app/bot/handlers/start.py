"""Онбординг — /start."""
from __future__ import annotations

from aiogram import F, Router
from aiogram.filters import CommandStart
from aiogram.types import Message
from sqlalchemy.ext.asyncio import AsyncSession

from app.bot.keyboards import start_inline
from app.common.logger import get_logger
from app.db.models.client import Client
from app.db.models.dialog import Dialog
from app.db.repositories.messages import save_outgoing
from app.domain.enums import DialogStage, MessageSender

router = Router(name="start")

log = get_logger(__name__)

GREETING = (
    "Здравствуйте! Вас приветствует <b>Центр Коррекции Речи Марии Анцевой</b> 🌿\n\n"
    "Я виртуальный помощник. Помогу записать ребёнка на диагностику, подобрать формат "
    "занятий и ответить на вопросы.\n\n"
    "Подскажите, как к Вам обращаться?"
)


@router.message(CommandStart())
async def cmd_start(
    message: Message,
    client: Client,  # noqa: ARG001
    dialog: Dialog,
    session: AsyncSession,
) -> None:
    dialog.current_stage = DialogStage.GREETING
    sent = await message.answer(GREETING, reply_markup=start_inline())
    await save_outgoing(
        session,
        dialog_id=dialog.id,
        sender=MessageSender.BOT,
        content=GREETING,
        tg_message_id=sent.message_id,
    )
    log.info("start_sent", dialog_id=dialog.id)


@router.callback_query(F.data == "role:parent")
async def cb_role_parent(callback) -> None:  # type: ignore[no-untyped-def]
    await callback.answer()
    await callback.message.edit_reply_markup(reply_markup=None)
    await callback.message.answer("Замечательно! Как Вас зовут?")


@router.callback_query(F.data == "role:teen")
async def cb_role_teen(callback) -> None:  # type: ignore[no-untyped-def]
    await callback.answer()
    await callback.message.edit_reply_markup(reply_markup=None)
    await callback.message.answer(
        "Спасибо, что написали. Для начала занятий потребуется, чтобы один из родителей "
        "связался с нами напрямую. Попросите, пожалуйста, маму или папу написать нам в "
        "этот же чат — мы всё обсудим и подберём удобное время. 🌿"
    )
