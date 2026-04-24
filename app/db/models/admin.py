"""Администратор / владелец / специалист — тот, кто работает из админки."""
from __future__ import annotations

from sqlalchemy import BigInteger, Boolean, Enum, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, TimestampMixin
from app.domain.enums import AdminRole


class Admin(Base, TimestampMixin):
    __tablename__ = "admins"

    id: Mapped[int] = mapped_column(primary_key=True)

    tg_user_id: Mapped[int] = mapped_column(BigInteger, unique=True, index=True)
    tg_username: Mapped[str | None] = mapped_column(String(64))
    name: Mapped[str] = mapped_column(String(128))

    role: Mapped[AdminRole] = mapped_column(
        Enum(AdminRole, native_enum=False, length=16),
        default=AdminRole.ADMIN,
    )

    active: Mapped[bool] = mapped_column(Boolean, default=True)
