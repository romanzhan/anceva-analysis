"""Pydantic-модели уровня домена.

Отделены от SQLAlchemy-моделей (`app/db/models/`), чтобы:
- API / Mini App / LLM работали со стабильным контрактом;
- легко тестировать без БД.
"""
from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field

from app.domain.enums import (
    ClientState,
    DialogMode,
    DialogStage,
    Direction,
    Language,
    Source,
)


class _BaseDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True, frozen=False, extra="ignore")


class ClientDTO(_BaseDTO):
    id: int
    tg_user_id: int
    phone: str | None = None
    name: str | None = None
    source: Source = Source.UNKNOWN
    state: ClientState = ClientState.NEW
    locale: Language = Language.RU
    referrer_client_id: int | None = None
    pd_consent_at: datetime | None = None
    created_at: datetime
    last_seen_at: datetime | None = None


class ChildDTO(_BaseDTO):
    id: int
    client_id: int
    full_name: str | None = None
    dob: date | None = None
    home_language: Language = Language.RU
    main_direction: Direction | None = None
    assigned_specialist_id: int | None = None


class DialogDTO(_BaseDTO):
    id: int
    client_id: int
    mode: DialogMode = DialogMode.BOT
    current_stage: DialogStage = DialogStage.GREETING
    taken_by_admin_id: int | None = None
    started_at: datetime
    last_activity_at: datetime


class MessageDTO(_BaseDTO):
    id: int
    dialog_id: int
    direction: str
    sender: str
    type: str
    content: str | None = None
    media_file_id: str | None = None
    media_transcript: str | None = None
    created_at: datetime


# -------- Извлечённые из диалога факты ----------------------------------------

class ExtractedChild(BaseModel):
    """Данные о ребёнке, извлечённые LLM из диалога."""

    full_name: str | None = None
    age_years: int | None = Field(default=None, ge=0, le=18)
    age_months: int | None = Field(default=None, ge=0, le=11)
    dob: date | None = None
    home_language: Language | None = None
    kindergarten: bool | None = None
    day_sleep_time: str | None = None
    diagnoses: list[str] = Field(default_factory=list)
    medical_docs_mentioned: bool = False


class ExtractedRequest(BaseModel):
    """Запрос родителя."""

    primary_direction: Direction | None = None
    specific_concerns: list[str] = Field(default_factory=list)
    parent_anxieties: list[str] = Field(default_factory=list)


class ExtractedFacts(BaseModel):
    """Структурированные факты после одного шага диалога."""

    parent_name: str | None = None
    child: ExtractedChild = Field(default_factory=ExtractedChild)
    request: ExtractedRequest = Field(default_factory=ExtractedRequest)


# -------- Слоты и окна для записи на ДИ --------------------------------------

class Slot(BaseModel):
    """Свободное окно у специалиста."""

    at: datetime
    specialist_id: int
    specialist_name: str
    duration_min: int = 90


# -------- Данные оплаты -------------------------------------------------------

class InvoiceLine(BaseModel):
    description: str
    amount: Decimal
