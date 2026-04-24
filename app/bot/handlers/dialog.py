"""Catch-all текстовый хендлер — пускает сообщение через LLM-роутер."""
from __future__ import annotations

import asyncio

from aiogram import Router
from aiogram.enums import ChatAction
from aiogram.types import Message
from sqlalchemy.ext.asyncio import AsyncSession

from app.common.config import get_settings
from app.common.logger import get_logger
from app.db.models.client import Client
from app.db.models.dialog import Dialog
from app.db.repositories.messages import save_incoming, save_outgoing
from app.dialog.router import process_turn
from app.domain.enums import DialogMode, MessageSender, MessageType

router = Router(name="dialog")
log = get_logger(__name__)


@router.message()
async def handle_text(
    message: Message,
    client: Client,  # noqa: ARG001
    dialog: Dialog,
    session: AsyncSession,
) -> None:
    text = (message.text or message.caption or "").strip()
    if not text:
        # медиа без подписи — обработают media-хендлеры; если ничего не подошло — игнор
        return

    await save_incoming(
        session,
        dialog_id=dialog.id,
        tg_message_id=message.message_id,
        type_=MessageType.TEXT,
        content=text,
    )

    # Если admin взял диалог — не отвечаем
    if dialog.mode is DialogMode.ADMIN:
        log.info("skip_admin_mode", dialog_id=dialog.id)
        return

    # Индикация «печатает…»
    typing_task = asyncio.create_task(_keep_typing(message))

    try:
        result = await process_turn(
            session, client=client, dialog=dialog, user_text=text
        )
    finally:
        typing_task.cancel()

    # Shadow mode: бот не отправляет, только логирует и показывает админу.
    # Пока без реализации на стороне админ-бота — просто флаг в лог.
    settings = get_settings()
    if settings.feature_shadow_mode and not result.escalated:
        log.info(
            "shadow_mode_draft",
            dialog_id=dialog.id,
            reply=result.reply_texts,
            confidence=result.confidence,
        )
        # Пока работает shadow — отправляем всё равно, но с пометкой.
        # Позже: не отправлять вовсе, ждать approve от админа.

    for txt in result.reply_texts:
        sent = await message.answer(txt)
        await save_outgoing(
            session,
            dialog_id=dialog.id,
            sender=MessageSender.BOT,
            content=txt,
            tg_message_id=sent.message_id,
        )

    if result.escalated:
        # TODO: нотифицировать админ-бот (сделаем на этапе admin_bot)
        log.info("dialog_escalated_notify_admin", dialog_id=dialog.id, reason=result.escalate_reason)


async def _keep_typing(message: Message) -> None:
    """Держит 'печатает...' пока не отменят (LLM-вызов может идти 5-15 сек)."""
    try:
        while True:
            await message.bot.send_chat_action(message.chat.id, ChatAction.TYPING)
            await asyncio.sleep(4)
    except asyncio.CancelledError:
        pass
