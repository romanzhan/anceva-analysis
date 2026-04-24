"""Оркестратор одного хода диалога.

Шаг:
1. Сохранить входящее сообщение.
2. Проверить hard-эскалацию → если да, уйти в mode=admin.
3. Собрать контекст (история + факты) → вызвать Gemini.
4. Применить результат: обновить факты, сменить stage, проверить soft-эскалацию.
5. Сохранить и отправить ответы.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.common.clock import now_utc
from app.common.errors import DialogEscalateError, LLMError
from app.common.logger import get_logger
from app.db.models.client import Client
from app.db.models.dialog import Dialog
from app.db.models.message import Message
from app.db.repositories.messages import recent_for_dialog
from app.dialog.escalation import should_soft_escalate, trigger_hard_escalation
from app.domain.enums import DialogMode, DialogStage, MessageSender
from app.llm.client import DialogTurn, get_llm_client
from app.llm.schemas import LLMReply

log = get_logger(__name__)


@dataclass(slots=True)
class DialogTurnResult:
    """Что на выходе одного хода — для handler'а бота."""

    reply_texts: list[str] = field(default_factory=list)
    next_stage: DialogStage | None = None
    escalated: bool = False
    escalate_reason: str | None = None
    confidence: float = 1.0
    requested_media: list[str] = field(default_factory=list)


async def process_turn(
    session: AsyncSession,
    *,
    client: Client,
    dialog: Dialog,
    user_text: str,
) -> DialogTurnResult:
    """Один ход: сообщение клиента → ответ бота (или эскалация)."""

    # --- 0. mode=admin — бот молчит --------------------------------------
    if dialog.mode is DialogMode.ADMIN:
        log.info("dialog_in_admin_mode_skip", dialog_id=dialog.id)
        return DialogTurnResult()

    # --- 1. Hard escalation (ключевые слова, жалобы) ---------------------
    if hard := trigger_hard_escalation(user_text):
        await _escalate(dialog, reason=hard)
        return DialogTurnResult(
            reply_texts=[
                "Я передам Ваше обращение Марии Сергеевне, она свяжется с Вами в течение дня 🌿"
            ],
            escalated=True,
            escalate_reason=hard,
        )

    # --- 2. Собираем контекст для LLM ------------------------------------
    history = await _build_history(session, dialog.id, last_user_text=user_text)
    facts = dict(dialog.facts or {})

    # --- 3. Вызов LLM ----------------------------------------------------
    try:
        reply = await get_llm_client().generate_reply(
            history=history,
            stage=dialog.current_stage.value,
            client_facts=facts,
        )
    except LLMError as exc:
        log.error("llm_failed", dialog_id=dialog.id, error=str(exc))
        await _escalate(dialog, reason=f"LLM error: {exc}")
        return DialogTurnResult(
            reply_texts=[
                "Минуточку, сейчас передам Вас нашему администратору 🌿"
            ],
            escalated=True,
            escalate_reason=f"llm_error: {exc}",
        )

    # --- 4. Применяем результат ------------------------------------------
    _merge_facts(dialog, reply)

    if reply.next_stage is not None:
        dialog.current_stage = reply.next_stage

    # LLM сама просит передать
    if reply.escalate:
        await _escalate(dialog, reason=reply.escalate_reason or "llm_requested")
        return DialogTurnResult(
            reply_texts=reply.reply
            or ["Минуту, я позову администратора — она ответит Вам лично 🌿"],
            escalated=True,
            escalate_reason=reply.escalate_reason,
            confidence=reply.confidence,
        )

    # Soft-эскалация по тексту пользователя (эмоции) — как защита
    if soft := should_soft_escalate(user_text):
        await _escalate(dialog, reason=soft, soft=True)
        return DialogTurnResult(
            reply_texts=reply.reply,
            escalated=True,
            escalate_reason=soft,
            confidence=reply.confidence,
        )

    dialog.last_activity_at = now_utc()

    return DialogTurnResult(
        reply_texts=reply.reply,
        next_stage=reply.next_stage,
        confidence=reply.confidence,
        requested_media=reply.requested_media,
    )


# ------------------------------------------------------------------------

async def _build_history(
    session: AsyncSession, dialog_id: int, *, last_user_text: str
) -> list[DialogTurn]:
    """Последние N сообщений + текущее (оно ещё не сохранено)."""
    past = await recent_for_dialog(session, dialog_id, limit=30)
    history = [_message_to_turn(m) for m in past if m.content or m.media_transcript]
    history.append(DialogTurn(role="user", text=last_user_text))
    return history


def _message_to_turn(msg: Message) -> DialogTurn:
    role = "user" if msg.sender is MessageSender.CLIENT else "model"
    text = msg.content or msg.media_transcript or ""
    return DialogTurn(role=role, text=text)


def _merge_facts(dialog: Dialog, reply: LLMReply) -> None:
    """Обновляем накопленные факты. Непустые новые значения перекрывают старые."""
    acc: dict[str, Any] = dict(dialog.facts or {})
    extracted = reply.extracted.model_dump(exclude_none=True, exclude_defaults=False)
    _deep_update(acc, extracted)
    dialog.facts = acc


def _deep_update(dst: dict[str, Any], src: dict[str, Any]) -> None:
    for k, v in src.items():
        if isinstance(v, dict) and isinstance(dst.get(k), dict):
            _deep_update(dst[k], v)
        elif v or v is False or v == 0:  # не затираем значением None / []
            dst[k] = v


async def _escalate(dialog: Dialog, *, reason: str, soft: bool = False) -> None:
    dialog.mode = DialogMode.ADMIN
    dialog.taken_at = None  # возьмёт конкретный админ позже
    dialog.taken_by_admin_id = None
    facts = dict(dialog.facts or {})
    facts["escalated_at"] = now_utc().isoformat()
    facts["escalate_reason"] = reason
    facts["escalate_soft"] = soft
    dialog.facts = facts
    raise_if_needed = DialogEscalateError(reason, soft=soft)
    log.info("dialog_escalated", dialog_id=dialog.id, reason=reason, soft=soft)
    # DialogEscalateError не бросаем, чтобы handler мог спокойно отправить reply
    _ = raise_if_needed  # статический чекер не ругается
