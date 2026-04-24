"""Обработка медиа — голос, фото, видео, документы.

Скачиваем file_id → Gemini описывает/транскрибирует → кладём результат как text
в тот же диалоговый роутер, как будто клиент написал текст.
"""
from __future__ import annotations

import asyncio

from aiogram import Bot, F, Router
from aiogram.enums import ChatAction
from aiogram.types import Message
from sqlalchemy.ext.asyncio import AsyncSession

from app.common.errors import LLMError
from app.common.logger import get_logger
from app.db.models.client import Client
from app.db.models.dialog import Dialog
from app.db.repositories.messages import save_incoming, save_outgoing
from app.dialog.router import process_turn
from app.domain.enums import DialogMode, MessageSender, MessageType
from app.llm.multimodal import describe_photo, describe_video, transcribe_voice

router = Router(name="media")
log = get_logger(__name__)


@router.message(F.voice | F.audio)
async def handle_voice(
    message: Message,
    bot: Bot,
    client: Client,  # noqa: ARG001
    dialog: Dialog,
    session: AsyncSession,
) -> None:
    file_id = (message.voice or message.audio).file_id  # type: ignore[union-attr]
    transcript = await _safe_call(
        transcribe_voice(bot, file_id),
        fallback="[не удалось распознать голосовое]",
    )
    await _ingest_and_reply(
        message=message,
        dialog=dialog,
        client=client,
        session=session,
        type_=MessageType.VOICE,
        file_id=file_id,
        transcript=transcript,
    )


@router.message(F.photo)
async def handle_photo(
    message: Message,
    bot: Bot,
    client: Client,
    dialog: Dialog,
    session: AsyncSession,
) -> None:
    assert message.photo is not None
    photo = message.photo[-1]  # самое большое
    caption = (message.caption or "").lower()

    # Эвристика: если в подписи есть "чек" / "оплата" / "каспи" — это чек
    purpose = "child"
    if any(k in caption for k in ("чек", "оплат", "каспи", "kaspi")):
        purpose = "check"
    elif any(k in caption for k in ("заключен", "невропатол", "врач", "диагноз")):
        purpose = "doc"

    transcript = await _safe_call(
        describe_photo(bot, photo.file_id, purpose=purpose),
        fallback="[фото получено, но не удалось описать]",
    )
    transcript = f"[фото · {purpose}] {transcript}"

    await _ingest_and_reply(
        message=message,
        dialog=dialog,
        client=client,
        session=session,
        type_=MessageType.PHOTO,
        file_id=photo.file_id,
        transcript=transcript,
    )


@router.message(F.video | F.video_note)
async def handle_video(
    message: Message,
    bot: Bot,
    client: Client,
    dialog: Dialog,
    session: AsyncSession,
) -> None:
    file_id = (message.video or message.video_note).file_id  # type: ignore[union-attr]
    transcript = await _safe_call(
        describe_video(bot, file_id),
        fallback="[видео получено, но не удалось описать]",
    )
    transcript = f"[видео] {transcript}"

    await _ingest_and_reply(
        message=message,
        dialog=dialog,
        client=client,
        session=session,
        type_=MessageType.VIDEO,
        file_id=file_id,
        transcript=transcript,
    )


async def _ingest_and_reply(
    *,
    message: Message,
    dialog: Dialog,
    client: Client,
    session: AsyncSession,
    type_: MessageType,
    file_id: str,
    transcript: str,
) -> None:
    """Сохранить медиа-сообщение с транскриптом и дёрнуть LLM на следующий ход."""
    msg = await save_incoming(
        session,
        dialog_id=dialog.id,
        tg_message_id=message.message_id,
        type_=type_,
        content=None,
        media_file_id=file_id,
    )
    msg.media_transcript = transcript
    await session.flush()

    if dialog.mode is DialogMode.ADMIN:
        return

    typing_task = asyncio.create_task(_keep_typing(message))
    try:
        result = await process_turn(
            session, client=client, dialog=dialog, user_text=transcript
        )
    finally:
        typing_task.cancel()

    for txt in result.reply_texts:
        sent = await message.answer(txt)
        await save_outgoing(
            session,
            dialog_id=dialog.id,
            sender=MessageSender.BOT,
            content=txt,
            tg_message_id=sent.message_id,
        )


async def _safe_call(coro, *, fallback: str) -> str:
    try:
        return await coro
    except LLMError as exc:
        log.warning("media_llm_failed", error=str(exc))
        return fallback
    except Exception as exc:  # noqa: BLE001
        log.exception("media_unexpected", error=str(exc))
        return fallback


async def _keep_typing(message: Message) -> None:
    try:
        while True:
            await message.bot.send_chat_action(message.chat.id, ChatAction.TYPING)
            await asyncio.sleep(4)
    except asyncio.CancelledError:
        pass
