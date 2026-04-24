"""Тесты LLM-схемы ответа."""
from __future__ import annotations

from app.domain.enums import DialogStage, Direction
from app.llm.schemas import LLMReply


def test_llm_reply_minimal() -> None:
    r = LLMReply.model_validate(
        {
            "reply": ["Здравствуйте!"],
            "next_stage": DialogStage.GOT_PARENT_NAME.value,
            "escalate": False,
            "confidence": 0.9,
        }
    )
    assert r.reply == ["Здравствуйте!"]
    assert r.next_stage is DialogStage.GOT_PARENT_NAME
    assert not r.escalate


def test_llm_reply_with_extraction() -> None:
    r = LLMReply.model_validate(
        {
            "reply": ["Спасибо, Айгерим!"],
            "extracted": {
                "parent_name": "Айгерим",
                "child": {"age_years": 1, "age_months": 8},
                "request": {"primary_direction": Direction.SPEECH_LAUNCH.value},
            },
            "next_stage": DialogStage.BRANCHING.value,
        }
    )
    assert r.extracted.parent_name == "Айгерим"
    assert r.extracted.child.age_years == 1
    assert r.extracted.request.primary_direction is Direction.SPEECH_LAUNCH
