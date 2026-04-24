"""Диалог родителя с ботом — долгоживущая сущность (один на клиента)."""
from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Any

from sqlalchemy import JSON, DateTime, Enum, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.db.base import Base, TimestampMixin
from app.domain.enums import DialogMode, DialogStage

if TYPE_CHECKING:
    from app.db.models.admin import Admin
    from app.db.models.client import Client
    from app.db.models.message import Message


class Dialog(Base, TimestampMixin):
    __tablename__ = "dialogs"

    id: Mapped[int] = mapped_column(primary_key=True)

    client_id: Mapped[int] = mapped_column(
        ForeignKey("clients.id", ondelete="CASCADE"), index=True
    )

    mode: Mapped[DialogMode] = mapped_column(
        Enum(DialogMode, native_enum=False, length=8),
        default=DialogMode.BOT,
        index=True,
    )
    current_stage: Mapped[DialogStage] = mapped_column(
        Enum(DialogStage, native_enum=False, length=32),
        default=DialogStage.GREETING,
        index=True,
    )

    # Когда и кем забрали у бота
    taken_by_admin_id: Mapped[int | None] = mapped_column(
        ForeignKey("admins.id", ondelete="SET NULL")
    )
    taken_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    # Контекст, который LLM накопил по диалогу (извлечённые факты)
    facts: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)

    started_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    last_activity_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), index=True
    )

    client: Mapped[Client] = relationship(back_populates="dialogs")
    taken_by: Mapped[Admin | None] = relationship()
    messages: Mapped[list[Message]] = relationship(
        back_populates="dialog",
        cascade="all,delete-orphan",
        order_by="Message.created_at",
    )

    def __repr__(self) -> str:
        return f"<Dialog id={self.id} client={self.client_id} stage={self.current_stage}>"
