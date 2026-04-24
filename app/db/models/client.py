"""Родитель (или подросток, если пишет сам)."""
from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import BigInteger, DateTime, Enum, ForeignKey, Index, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin
from app.domain.enums import ClientState, Language, Source

if TYPE_CHECKING:
    from app.db.models.child import Child
    from app.db.models.dialog import Dialog
    from app.db.models.payment import Payment


class Client(Base, TimestampMixin):
    __tablename__ = "clients"

    id: Mapped[int] = mapped_column(primary_key=True)

    # Контакты
    tg_user_id: Mapped[int] = mapped_column(BigInteger, unique=True, index=True)
    tg_username: Mapped[str | None] = mapped_column(String(64))
    phone: Mapped[str | None] = mapped_column(String(32), index=True)
    name: Mapped[str | None] = mapped_column(String(128))

    # Воронка
    state: Mapped[ClientState] = mapped_column(
        Enum(ClientState, native_enum=False, length=32),
        default=ClientState.NEW,
        index=True,
    )
    source: Mapped[Source] = mapped_column(
        Enum(Source, native_enum=False, length=32),
        default=Source.UNKNOWN,
    )
    locale: Mapped[Language] = mapped_column(
        Enum(Language, native_enum=False, length=8),
        default=Language.RU,
    )

    # Рефералка
    referrer_client_id: Mapped[int | None] = mapped_column(
        ForeignKey("clients.id", ondelete="SET NULL")
    )

    # Правовое
    pd_consent_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    pd_consent_version: Mapped[str | None] = mapped_column(String(16))

    last_seen_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), index=True)

    children: Mapped[list[Child]] = relationship(back_populates="client", cascade="all,delete-orphan")
    dialogs: Mapped[list[Dialog]] = relationship(back_populates="client", cascade="all,delete-orphan")
    payments: Mapped[list[Payment]] = relationship(back_populates="client")

    __table_args__ = (
        Index("ix_clients_state_last_seen", "state", "last_seen_at"),
    )

    def __repr__(self) -> str:
        return f"<Client id={self.id} tg={self.tg_user_id} name={self.name!r}>"
