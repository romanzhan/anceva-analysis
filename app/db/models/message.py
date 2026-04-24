"""Сообщение в диалоге — в обе стороны, любого типа."""
from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Any

from sqlalchemy import JSON, BigInteger, DateTime, Enum, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.db.base import Base
from app.domain.enums import MessageDirection, MessageSender, MessageType

if TYPE_CHECKING:
    from app.db.models.dialog import Dialog


class Message(Base):
    __tablename__ = "messages"

    id: Mapped[int] = mapped_column(primary_key=True)

    dialog_id: Mapped[int] = mapped_column(
        ForeignKey("dialogs.id", ondelete="CASCADE"), index=True
    )

    direction: Mapped[MessageDirection] = mapped_column(
        Enum(MessageDirection, native_enum=False, length=8)
    )
    sender: Mapped[MessageSender] = mapped_column(
        Enum(MessageSender, native_enum=False, length=16)
    )
    type: Mapped[MessageType] = mapped_column(
        Enum(MessageType, native_enum=False, length=16), default=MessageType.TEXT
    )

    # Telegram side
    tg_message_id: Mapped[int | None] = mapped_column(BigInteger)

    # Payload
    content: Mapped[str | None] = mapped_column(Text)
    media_file_id: Mapped[str | None] = mapped_column(String(256))
    media_transcript: Mapped[str | None] = mapped_column(Text)

    # Что LLM извлёк (после обработки исходящих сообщений пользователя)
    extracted: Mapped[dict[str, Any] | None] = mapped_column(JSON)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), index=True
    )

    dialog: Mapped[Dialog] = relationship(back_populates="messages")

    def __repr__(self) -> str:
        preview = (self.content or "")[:40]
        return f"<Message id={self.id} {self.direction}/{self.type}: {preview!r}>"
