"""Педагог / специалист центра."""
from __future__ import annotations

from typing import Any

from sqlalchemy import JSON, Boolean, Enum, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, TimestampMixin
from app.domain.enums import Language


class Specialist(Base, TimestampMixin):
    __tablename__ = "specialists"

    id: Mapped[int] = mapped_column(primary_key=True)

    name: Mapped[str] = mapped_column(String(128))
    title: Mapped[str | None] = mapped_column(String(128))  # "логопед-дефектолог"
    language: Mapped[Language] = mapped_column(
        Enum(Language, native_enum=False, length=8),
        default=Language.RU,
    )

    # Список направлений (Direction.value)
    directions: Mapped[list[str]] = mapped_column(JSON, default=list)

    # Расписание: словарь вида {"mon": ["09:00-13:00", "15:00-20:00"], ...}
    timetable: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)

    active: Mapped[bool] = mapped_column(Boolean, default=True)

    def __repr__(self) -> str:
        return f"<Specialist id={self.id} name={self.name!r}>"
