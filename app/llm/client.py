"""Клиент Gemini с structured output.

На входе — история сообщений и факты о клиенте.
На выходе — валидированный объект `LLMReply`.

Мультимодалку (голос/фото/видео) делаем отдельным проходом: каждое медиа описывается
моделью → транскрипт сохраняется в messages.media_transcript → уходит в основную сборку.
"""
from __future__ import annotations

import asyncio
import json
from dataclasses import dataclass
from typing import Any

import google.generativeai as genai
from google.generativeai.types import GenerationConfig
from pydantic import ValidationError

from app.common.config import get_settings
from app.common.errors import LLMBadResponseError, LLMError, LLMTimeoutError
from app.common.logger import get_logger
from app.llm.prompts.master import MASTER_PROMPT, build_stage_hint
from app.llm.schemas import LLMReply

log = get_logger(__name__)

_settings = get_settings()

# Инициализация SDK один раз
if _settings.gemini_api_key.get_secret_value():
    genai.configure(api_key=_settings.gemini_api_key.get_secret_value())


@dataclass(slots=True)
class DialogTurn:
    """Одно сообщение в истории — в упрощённой форме для LLM."""

    role: str  # "user" | "model"
    text: str


class GeminiClient:
    """Асинхронная обёртка над google-generativeai."""

    def __init__(self, model_name: str | None = None) -> None:
        self.model_name = model_name or _settings.gemini_model_main
        self._model = genai.GenerativeModel(
            model_name=self.model_name,
            system_instruction=MASTER_PROMPT,
        )

    async def generate_reply(
        self,
        *,
        history: list[DialogTurn],
        stage: str,
        client_facts: dict[str, Any] | None = None,
    ) -> LLMReply:
        """Сгенерировать следующий ход бота.

        Args:
            history: последние N сообщений диалога в хронологическом порядке.
                     Последний элемент — самое свежее сообщение клиента.
            stage: текущая стадия FSM (значение DialogStage).
            client_facts: уже собранные факты о клиенте/ребёнке.
        """
        system_addendum = self._build_system_addendum(stage, client_facts or {})

        contents = self._history_to_contents(history, system_addendum)

        config = GenerationConfig(
            response_mime_type="application/json",
            response_schema=LLMReply.model_json_schema(),
            temperature=0.7,
            max_output_tokens=2048,
        )

        try:
            response = await asyncio.wait_for(
                self._model.generate_content_async(
                    contents=contents,
                    generation_config=config,
                ),
                timeout=_settings.gemini_timeout_sec,
            )
        except TimeoutError as exc:
            raise LLMTimeoutError("Gemini timeout") from exc
        except Exception as exc:  # noqa: BLE001 — SDK кидает разные типы
            raise LLMError(f"Gemini call failed: {exc}") from exc

        raw = response.text or ""
        try:
            parsed = json.loads(raw)
            return LLMReply.model_validate(parsed)
        except (json.JSONDecodeError, ValidationError) as exc:
            log.error("llm_bad_response", raw=raw[:500], error=str(exc))
            raise LLMBadResponseError(f"не удалось распарсить ответ: {exc}") from exc

    @staticmethod
    def _build_system_addendum(stage: str, facts: dict[str, Any]) -> str:
        parts = [f"Текущая стадия: {stage}", build_stage_hint(stage)]
        if facts:
            parts.append(f"Уже известные факты: {json.dumps(facts, ensure_ascii=False)}")
        return "\n".join(parts)

    @staticmethod
    def _history_to_contents(
        history: list[DialogTurn],
        system_addendum: str,
    ) -> list[dict[str, Any]]:
        """Преобразует историю в формат contents для Gemini."""
        contents: list[dict[str, Any]] = []
        if system_addendum:
            contents.append({"role": "user", "parts": [{"text": f"[контекст]\n{system_addendum}"}]})
            contents.append({"role": "model", "parts": [{"text": "Понял, продолжаю."}]})

        for turn in history:
            contents.append({"role": turn.role, "parts": [{"text": turn.text}]})
        return contents


# Синглтон, создаётся при первом доступе
_client: GeminiClient | None = None


def get_llm_client() -> GeminiClient:
    global _client
    if _client is None:
        _client = GeminiClient()
    return _client
