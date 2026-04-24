"""Сидинг первого админа по OWNER_TG_USER_ID из .env.

Запуск: python -m scripts.seed_owner
Идемпотентен: повторный запуск ничего не делает.
"""
from __future__ import annotations

import asyncio

from sqlalchemy import select

from app.common.config import get_settings
from app.common.logger import configure_logging, get_logger
from app.db.models.admin import Admin
from app.db.session import session_scope
from app.domain.enums import AdminRole


async def main() -> None:
    configure_logging()
    log = get_logger("seed")
    settings = get_settings()

    if not settings.owner_tg_user_id:
        log.error("owner_tg_user_id_not_set")
        raise SystemExit(1)

    async with session_scope() as session:
        existing = await session.execute(
            select(Admin).where(Admin.tg_user_id == settings.owner_tg_user_id)
        )
        if existing.scalar_one_or_none():
            log.info("owner_already_exists")
            return

        session.add(
            Admin(
                tg_user_id=settings.owner_tg_user_id,
                name="Owner",
                role=AdminRole.OWNER,
                active=True,
            )
        )
        log.info("owner_created", tg_user_id=settings.owner_tg_user_id)


if __name__ == "__main__":
    asyncio.run(main())
