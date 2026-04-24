"""Операции с таблицей clients."""
from __future__ import annotations

from aiogram.types import User as TgUser
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.common.clock import now_utc
from app.db.models.client import Client
from app.db.models.dialog import Dialog
from app.domain.enums import ClientState, Language, Source


async def get_by_tg_user_id(session: AsyncSession, tg_user_id: int) -> Client | None:
    result = await session.execute(select(Client).where(Client.tg_user_id == tg_user_id))
    return result.scalar_one_or_none()


async def upsert_from_tg(
    session: AsyncSession,
    tg_user: TgUser,
    *,
    source: Source = Source.UNKNOWN,
) -> tuple[Client, bool]:
    """Создаёт клиента по данным Telegram-пользователя или обновляет last_seen.

    Returns: (client, created)
    """
    existing = await get_by_tg_user_id(session, tg_user.id)
    now = now_utc()
    if existing is not None:
        existing.last_seen_at = now
        if tg_user.username and existing.tg_username != tg_user.username:
            existing.tg_username = tg_user.username
        return existing, False

    client = Client(
        tg_user_id=tg_user.id,
        tg_username=tg_user.username,
        name=_full_name(tg_user),
        source=source,
        locale=Language.RU,
        state=ClientState.NEW,
        last_seen_at=now,
    )
    session.add(client)
    await session.flush()
    return client, True


async def get_or_create_dialog(session: AsyncSession, client_id: int) -> Dialog:
    """Один долгоживущий диалог на клиента."""
    result = await session.execute(
        select(Dialog).where(Dialog.client_id == client_id)
    )
    dialog = result.scalar_one_or_none()
    if dialog is not None:
        return dialog

    dialog = Dialog(client_id=client_id)
    session.add(dialog)
    await session.flush()
    return dialog


def _full_name(user: TgUser) -> str | None:
    parts = [p for p in (user.first_name, user.last_name) if p]
    return " ".join(parts) if parts else None
