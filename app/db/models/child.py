"""Ребёнок. Отдельная сущность — у одной мамы может быть двое-трое, и наоборот."""
from __future__ import annotations

from datetime import date
from typing import TYPE_CHECKING

from sqlalchemy import Date, Enum, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin
from app.domain.enums import Direction, Language

if TYPE_CHECKING:
    from app.db.models.anketa import Anketa
    from app.db.models.client import Client
    from app.db.models.diagnostic import Diagnostic
    from app.db.models.lesson import Lesson
    from app.db.models.specialist import Specialist


class Child(Base, TimestampMixin):
    __tablename__ = "children"

    id: Mapped[int] = mapped_column(primary_key=True)

    client_id: Mapped[int] = mapped_column(
        ForeignKey("clients.id", ondelete="CASCADE"), index=True
    )

    full_name: Mapped[str | None] = mapped_column(String(256))
    dob: Mapped[date | None] = mapped_column(Date, index=True)
    gender: Mapped[str | None] = mapped_column(String(1))  # m / f / null

    home_language: Mapped[Language] = mapped_column(
        Enum(Language, native_enum=False, length=8),
        default=Language.RU,
    )

    main_direction: Mapped[Direction | None] = mapped_column(
        Enum(Direction, native_enum=False, length=32),
        index=True,
    )

    assigned_specialist_id: Mapped[int | None] = mapped_column(
        ForeignKey("specialists.id", ondelete="SET NULL")
    )

    notes: Mapped[str | None] = mapped_column(String(2000))

    client: Mapped[Client] = relationship(back_populates="children")
    anketa: Mapped[Anketa | None] = relationship(
        back_populates="child", uselist=False, cascade="all,delete-orphan"
    )
    diagnostics: Mapped[list[Diagnostic]] = relationship(back_populates="child")
    lessons: Mapped[list[Lesson]] = relationship(back_populates="child")
    specialist: Mapped[Specialist | None] = relationship()

    def __repr__(self) -> str:
        return f"<Child id={self.id} name={self.full_name!r}>"
