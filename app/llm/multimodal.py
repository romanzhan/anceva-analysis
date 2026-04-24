"""Мультимодальная обработка: голос, фото, документы.

Принимает Telegram file_id, скачивает через Bot API, передаёт в Gemini как inline bytes.
Возвращает текстовый транскрипт / описание.
"""
from __future__ import annotations

import asyncio
from io import BytesIO

import google.generativeai as genai
from aiogram import Bot

from app.common.config import get_settings
from app.common.errors import LLMError
from app.common.logger import get_logger

log = get_logger(__name__)
_settings = get_settings()


async def transcribe_voice(bot: Bot, file_id: str) -> str:
    """Транскрибирует голосовое сообщение Telegram → русский текст."""
    audio_bytes = await _download_file(bot, file_id)
    model = genai.GenerativeModel(_settings.gemini_model_main)
    prompt = (
        "Ты — транскрибатор. Верни только точный текст того, что говорит человек на русском. "
        "Без комментариев, без перевода, без разметки. Если язык другой — транслитерируй фонетически."
    )
    try:
        response = await asyncio.wait_for(
            model.generate_content_async(
                [prompt, {"mime_type": "audio/ogg", "data": audio_bytes}]
            ),
            timeout=_settings.gemini_timeout_sec,
        )
    except Exception as exc:  # noqa: BLE001
        raise LLMError(f"voice transcribe failed: {exc}") from exc

    return (response.text or "").strip()


async def describe_photo(bot: Bot, file_id: str, purpose: str = "child") -> str:
    """Описывает фото.

    purpose:
      "child" — общее описание: что делает ребёнок, эмоции, обстановка.
      "doc"   — извлечение текста из медицинского заключения.
      "check" — распознавание суммы и даты из Kaspi-чека.
    """
    image_bytes = await _download_file(bot, file_id)
    model = genai.GenerativeModel(_settings.gemini_model_main)
    prompts = {
        "child": (
            "На фото — ребёнок. Опиши: возраст (примерно), что делает, выражение лица, "
            "обстановка. Без медицинских выводов. 2–3 предложения."
        ),
        "doc": (
            "На фото — медицинский документ (заключение врача, результаты обследования). "
            "Извлеки и верни в простом виде: кем выдан, дата, диагноз, назначения. "
            "Если не читается — напиши 'не удалось распознать'."
        ),
        "check": (
            "На фото — чек Kaspi об оплате. Извлеки ТОЛЬКО: сумма (число), дата, "
            "последние 4 цифры номера транзакции. Формат: 'SUM=X DATE=Y TXN=Z'. "
            "Если не чек — 'не чек'."
        ),
    }
    prompt = prompts.get(purpose, prompts["child"])

    try:
        response = await asyncio.wait_for(
            model.generate_content_async(
                [prompt, {"mime_type": "image/jpeg", "data": image_bytes}]
            ),
            timeout=_settings.gemini_timeout_sec,
        )
    except Exception as exc:  # noqa: BLE001
        raise LLMError(f"photo describe failed: {exc}") from exc

    return (response.text or "").strip()


async def describe_video(bot: Bot, file_id: str) -> str:
    """Описывает видео ребёнка (для подготовки специалиста к ДИ)."""
    # Видео может быть тяжёлое — лимит Gemini inline ~20МБ.
    # При превышении — просто сохраняем file_id, специалист посмотрит в админке.
    video_bytes = await _download_file(bot, file_id, max_size_mb=20)
    if video_bytes is None:
        return "[видео слишком большое для авто-анализа, сохранено для специалиста]"

    model = genai.GenerativeModel(_settings.gemini_model_main)
    prompt = (
        "На видео — ребёнок. Кратко опиши: что делает, играет ли сам или с кем-то, "
        "есть ли речь/звукоподражания, какие эмоции. 3–5 предложений. "
        "Без диагнозов, только наблюдения."
    )
    try:
        response = await asyncio.wait_for(
            model.generate_content_async(
                [prompt, {"mime_type": "video/mp4", "data": video_bytes}]
            ),
            timeout=_settings.gemini_timeout_sec * 2,
        )
    except Exception as exc:  # noqa: BLE001
        raise LLMError(f"video describe failed: {exc}") from exc

    return (response.text or "").strip()


async def _download_file(
    bot: Bot, file_id: str, max_size_mb: float = 20
) -> bytes | None:
    """Скачать файл из Telegram. Возвращает None, если файл слишком большой."""
    try:
        file = await bot.get_file(file_id)
    except Exception as exc:  # noqa: BLE001
        raise LLMError(f"не удалось получить file_info: {exc}") from exc

    if file.file_size and file.file_size > max_size_mb * 1024 * 1024:
        log.warning("media_too_large", file_id=file_id, size=file.file_size)
        return None

    buf = BytesIO()
    await bot.download(file, destination=buf)
    return buf.getvalue()
