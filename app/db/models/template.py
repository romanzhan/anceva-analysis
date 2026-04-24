"""Текстовые шаблоны — переведённый в БД чек-лист.

Редактируются в веб-админке. Placeholders: {parent_name}, {child_name}, {slot}, {amount}...
"""
from __future__ import annotations

from sqlalchemy import JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, TimestampMixin


class Template(Base, TimestampMixin):
    __tablename__ = "templates"

    id: Mapped[int] = mapped_column(primary_key=True)

    slug: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    title: Mapped[str] = mapped_column(String(128))
    category: Mapped[str] = mapped_column(String(64), index=True)
    body: Mapped[str] = mapped_column(Text)
    placeholders: Mapped[list[str]] = mapped_column(JSON, default=list)

    version: Mapped[int] = mapped_column(default=1)
