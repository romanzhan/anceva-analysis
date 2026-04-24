"""Очередь отложенных задач для планировщика.

APScheduler реально исполняет, но очередь хранится здесь —
чтобы видеть в админке, что и когда улетит.
"""
from __future__ import annotations

from datetime import datetime
from typing import Any

from sqlalchemy import JSON, DateTime, Enum, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, TimestampMixin
from app.domain.enums import TaskKind, TaskStatus


class Task(Base, TimestampMixin):
    __tablename__ = "tasks"

    id: Mapped[int] = mapped_column(primary_key=True)

    client_id: Mapped[int | None] = mapped_column(
        ForeignKey("clients.id", ondelete="CASCADE"), index=True
    )

    kind: Mapped[TaskKind] = mapped_column(
        Enum(TaskKind, native_enum=False, length=32), index=True
    )
    status: Mapped[TaskStatus] = mapped_column(
        Enum(TaskStatus, native_enum=False, length=16),
        default=TaskStatus.PENDING,
        index=True,
    )

    fire_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
    payload: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)

    done_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    error: Mapped[str | None]
