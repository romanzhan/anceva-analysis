"""Handoff: админ берёт диалог / отдаёт боту / пересылает сообщения клиенту."""
from __future__ import annotations

from aiogram import F, Router
from aiogram.types import CallbackQuery

from app.common.logger import get_logger

router = Router(name="admin_handoff")
log = get_logger(__name__)


@router.callback_query(F.data.startswith("take:"))
async def cb_take(callback: CallbackQuery) -> None:
    """Админ жмёт «Взять» в уведомлении об эскалации."""
    await callback.answer("Беру…")
    dialog_id = int(callback.data.split(":", 1)[1])  # type: ignore[union-attr]
    # TODO:
    #   1. Пометить Dialog.taken_by_admin_id = admin.id
    #   2. Открыть приватный «мост»: все сообщения клиента пересылать сюда, а
    #      сообщения этого админа — пересылать клиенту через клиентского бота.
    log.info("admin_take", dialog_id=dialog_id, admin_tg=callback.from_user.id)
    await callback.message.answer(
        f"Ты взял(а) диалог #{dialog_id}. Напиши сюда ответ — я перешлю клиенту."
    )


@router.callback_query(F.data.startswith("view:"))
async def cb_view(callback: CallbackQuery) -> None:
    await callback.answer()
    dialog_id = int(callback.data.split(":", 1)[1])  # type: ignore[union-attr]
    # TODO: отдать последние N сообщений диалога с форматированием
    await callback.message.answer(f"История диалога #{dialog_id} — пока не реализовано.")


@router.callback_query(F.data.startswith("release:"))
async def cb_release(callback: CallbackQuery) -> None:
    await callback.answer("Отдал(а) боту.")
    dialog_id = int(callback.data.split(":", 1)[1])  # type: ignore[union-attr]
    # TODO: Dialog.mode = bot, taken_by_admin_id = None
    log.info("admin_release", dialog_id=dialog_id)
