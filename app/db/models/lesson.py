"""Регулярное занятие."""
from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, Enum, ForeignKey, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin
from app.domain.enums import LessonStatus

if TYPE_CHECKING:
    from app.db.models.child import Child
    from app.db.models.specialist import Specialist


class Lesson(Base, TimestampMixin):
    __tablename__ = "lessons"

    id: Mapped[int] = mapped_column(primary_key=True)

    child_id: Mapped[int] = mapped_column(
        ForeignKey("children.id", ondelete="CASCADE"), index=True
    )
    specialist_id: Mapped[int | None] = mapped_column(
        ForeignKey("specialists.id", ondelete="SET NULL")
    )

    scheduled_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
    duration_min: Mapped[int] = mapped_column(default=30)
    room: Mapped[str | None] = mapped_column(String(16))

    price: Mapped[Decimal] = mapped_column(Numeric(10, 2))
    status: Mapped[LessonStatus] = mapped_column(
        Enum(LessonStatus, native_enum=False, length=24),
        default=LessonStatus.PLANNED,
        index=True,
    )

    # Если перенесено — ссылка на новое занятие
    rescheduled_to_id: Mapped[int | None] = mapped_column(
        ForeignKey("lessons.id", ondelete="SET NULL")
    )

    # Когда клиент предупредил о пропуске (для правила «до 19:00»)
    notified_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    child: Mapped[Child] = relationship(back_populates="lessons")
    specialist: Mapped[Specialist | None] = relationship()
