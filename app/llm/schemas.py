"""Контракт ответа LLM.

Каждая реплика — JSON по этой схеме.
Gemini structured output применяется через Pydantic → JSON Schema.
"""
from __future__ import annotations

from pydantic import BaseModel, Field

from app.domain.enums import DialogStage, Direction


class ChildFacts(BaseModel):
    """Факты о ребёнке, которые модель услышала из последних сообщений."""

    full_name: str | None = None
    age_years: int | None = Field(default=None, ge=0, le=18)
    age_months: int | None = Field(default=None, ge=0, le=11)
    kindergarten: bool | None = None
    day_sleep_time: str | None = None
    diagnoses: list[str] = Field(default_factory=list)
    medical_docs_mentioned: bool = False


class RequestFacts(BaseModel):
    primary_direction: Direction | None = None
    specific_concerns: list[str] = Field(default_factory=list)
    parent_anxieties: list[str] = Field(default_factory=list)


class ExtractedFromTurn(BaseModel):
    """Что модель извлекла после одного хода диалога."""

    parent_name: str | None = None
    child: ChildFacts = Field(default_factory=ChildFacts)
    request: RequestFacts = Field(default_factory=RequestFacts)


class LLMReply(BaseModel):
    """Полный ответ модели за один ход."""

    # 1–3 коротких сообщения, которые бот пошлёт клиенту
    reply: list[str] = Field(default_factory=list, max_length=4)

    # Что извлекли из реплики пользователя
    extracted: ExtractedFromTurn = Field(default_factory=ExtractedFromTurn)

    # Куда переводим FSM
    next_stage: DialogStage | None = None

    # Нужно ли передать человеку
    escalate: bool = False
    escalate_reason: str | None = None

    # Уверенность модели в своём ответе (0..1)
    confidence: float = Field(default=1.0, ge=0.0, le=1.0)

    # Запрошенные медиа (бот отправит отдельно напоминание / кнопку)
    requested_media: list[str] = Field(default_factory=list)
