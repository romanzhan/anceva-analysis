"""Приём чеков Kaspi (фото с подписью или после кнопки «Прислать чек»)."""
from __future__ import annotations

from aiogram import F, Router
from aiogram.types import Message

from app.common.logger import get_logger

router = Router(name="payment")
log = get_logger(__name__)


@router.message(F.document & F.document.mime_type.startswith("image/"))
async def handle_doc_check(message: Message) -> None:
    # Клиенты иногда шлют чек как document, а не photo.
    # Обрабатывается вместе с photo в media-роутере; здесь заглушка.
    log.info("doc_check_received", file_id=message.document.file_id if message.document else None)
    await message.answer("Получили! Проверю оплату и напишу 🌿")
