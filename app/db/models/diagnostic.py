"""Первичная диагностика (ДИ)."""
from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, DateTime, Enum, ForeignKey, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin
from app.domain.enums import DiagnosticStatus, Direction, PaymentStatus

if TYPE_CHECKING:
    from app.db.models.child import Child
    from app.db.models.specialist import Specialist


class Diagnostic(Base, TimestampMixin):
    __tablename__ = "diagnostics"

    id: Mapped[int] = mapped_column(primary_key=True)

    child_id: Mapped[int] = mapped_column(
        ForeignKey("children.id", ondelete="CASCADE"), index=True
    )
    specialist_id: Mapped[int | None] = mapped_column(
        ForeignKey("specialists.id", ondelete="SET NULL")
    )

    direction: Mapped[Direction] = mapped_column(
        Enum(Direction, native_enum=False, length=32)
    )

    scheduled_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
    status: Mapped[DiagnosticStatus] = mapped_column(
        Enum(DiagnosticStatus, native_enum=False, length=16),
        default=DiagnosticStatus.BOOKED,
        index=True,
    )

    # Бронь
    price: Mapped[Decimal] = mapped_column(Numeric(10, 2))
    payment_status: Mapped[PaymentStatus] = mapped_column(
        Enum(PaymentStatus, native_enum=False, length=16),
        default=PaymentStatus.INVOICED,
    )
    transfer_count: Mapped[int] = mapped_column(default=0)  # сколько раз переносили

    # Подготовка
    anketa_received: Mapped[bool] = mapped_column(Boolean, default=False)
    videos_received: Mapped[bool] = mapped_column(Boolean, default=False)

    # После проведения
    result_note: Mapped[str | None] = mapped_column(Text)
    room: Mapped[str | None] = mapped_column(String(16))

    child: Mapped[Child] = relationship(back_populates="diagnostics")
    specialist: Mapped[Specialist | None] = relationship()
