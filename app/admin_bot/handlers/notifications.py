"""Нотификации админам о важных событиях.

Триггерятся из кода клиентского бота, из scheduler'а или из админки.
Здесь — сервисный API + минимальная обработка входящих callback'ов.
"""
from __future__ import annotations

from aiogram import Bot, Router
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from app.common.config import get_settings
from app.common.logger import get_logger

router = Router(name="admin_notifications")
log = get_logger(__name__)


async def notify_escalation(
    admin_bot: Bot,
    *,
    dialog_id: int,
    client_name: str | None,
    child_summary: str,
    reason: str,
    last_message: str,
) -> None:
    """Отправить уведомление об эскалации всем активным админам.

    В MVP отправляем только owner'у (из .env). Позже — списку из БД.
    """
    settings = get_settings()
    owner_id = settings.owner_tg_user_id
    if not owner_id:
        log.warning("no_owner_id_for_escalation")
        return

    text = (
        "🔔 <b>Эскалация</b>\n"
        f"Клиент: {client_name or '—'}\n"
        f"Ребёнок: {child_summary}\n"
        f"Причина: {reason}\n\n"
        f"<i>Последнее:</i> {last_message[:200]}"
    )
    kbd = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="Взять", callback_data=f"take:{dialog_id}"
                ),
                InlineKeyboardButton(
                    text="Посмотреть", callback_data=f"view:{dialog_id}"
                ),
            ]
        ]
    )
    try:
        await admin_bot.send_message(chat_id=owner_id, text=text, reply_markup=kbd)
    except Exception as exc:  # noqa: BLE001
        log.error("notify_failed", owner_id=owner_id, error=str(exc))
