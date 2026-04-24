"""Операции с сообщениями."""
from __future__ import annotations

from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.common.clock import now_utc
from app.db.models.message import Message
from app.domain.enums import MessageDirection, MessageSender, MessageType


async def save_incoming(
    session: AsyncSession,
    *,
    dialog_id: int,
    tg_message_id: int | None,
    type_: MessageType,
    content: str | None,
    media_file_id: str | None = None,
) -> Message:
    msg = Message(
        dialog_id=dialog_id,
        direction=MessageDirection.IN,
        sender=MessageSender.CLIENT,
        type=type_,
        tg_message_id=tg_message_id,
        content=content,
        media_file_id=media_file_id,
    )
    session.add(msg)
    await session.flush()
    return msg


async def save_outgoing(
    session: AsyncSession,
    *,
    dialog_id: int,
    sender: MessageSender,
    content: str,
    tg_message_id: int | None = None,
    type_: MessageType = MessageType.TEXT,
    extracted: dict[str, Any] | None = None,
) -> Message:
    msg = Message(
        dialog_id=dialog_id,
        direction=MessageDirection.OUT,
        sender=sender,
        type=type_,
        tg_message_id=tg_message_id,
        content=content,
        extracted=extracted,
    )
    session.add(msg)
    await session.flush()
    return msg


async def recent_for_dialog(
    session: AsyncSession,
    dialog_id: int,
    limit: int = 30,
) -> list[Message]:
    """Последние N сообщений для контекста LLM (возвращает в хронологическом порядке)."""
    result = await session.execute(
        select(Message)
        .where(Message.dialog_id == dialog_id)
        .order_by(Message.created_at.desc())
        .limit(limit)
    )
    msgs = list(result.scalars().all())
    msgs.reverse()
    return msgs


async def touch_dialog_activity(dialog: Any) -> None:
    dialog.last_activity_at = now_utc()
