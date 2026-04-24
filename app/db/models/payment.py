"""Оплата — месячный счёт или разовый (бронь ДИ, утренник)."""
from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, Enum, ForeignKey, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin
from app.domain.enums import PaymentMethod, PaymentStatus

if TYPE_CHECKING:
    from app.db.models.child import Child
    from app.db.models.client import Client


class Payment(Base, TimestampMixin):
    __tablename__ = "payments"

    id: Mapped[int] = mapped_column(primary_key=True)

    client_id: Mapped[int] = mapped_column(
        ForeignKey("clients.id", ondelete="CASCADE"), index=True
    )
    child_id: Mapped[int | None] = mapped_column(
        ForeignKey("children.id", ondelete="SET NULL")
    )

    # YYYY-MM для месячных, пусто для разовых
    period: Mapped[str | None] = mapped_column(String(7), index=True)

    amount: Mapped[Decimal] = mapped_column(Numeric(10, 2))
    method: Mapped[PaymentMethod] = mapped_column(
        Enum(PaymentMethod, native_enum=False, length=16),
        default=PaymentMethod.CASH,
    )
    status: Mapped[PaymentStatus] = mapped_column(
        Enum(PaymentStatus, native_enum=False, length=16),
        default=PaymentStatus.DRAFT,
        index=True,
    )

    description: Mapped[str | None] = mapped_column(Text)
    kaspi_check_file_id: Mapped[str | None] = mapped_column(String(256))

    invoiced_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    paid_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    client: Mapped[Client] = relationship(back_populates="payments")
