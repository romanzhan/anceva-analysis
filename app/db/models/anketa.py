"""Анкета ребёнка — заполняется в Mini App перед диагностикой."""
from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Any

from sqlalchemy import JSON, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.db.models.child import Child


class Anketa(Base, TimestampMixin):
    __tablename__ = "anketas"

    id: Mapped[int] = mapped_column(primary_key=True)

    child_id: Mapped[int] = mapped_column(
        ForeignKey("children.id", ondelete="CASCADE"),
        unique=True,
        index=True,
    )

    # Все ответы в JSON — схема может эволюционировать без миграции
    answers: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)

    # Ссылки на загруженные медиа (tg file_id)
    video_refs: Mapped[list[str]] = mapped_column(JSON, default=list)
    doc_refs: Mapped[list[str]] = mapped_column(JSON, default=list)

    filled_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    child: Mapped[Child] = relationship(back_populates="anketa")
