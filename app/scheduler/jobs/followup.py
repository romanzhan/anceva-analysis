"""Follow-up молчащих диалогов."""
from __future__ import annotations

from datetime import timedelta

from sqlalchemy import select

from app.common.clock import now_utc
from app.common.logger import get_logger
from app.db.models.dialog import Dialog
from app.db.session import session_scope
from app.domain.enums import DialogMode

log = get_logger(__name__)


async def check_silent_dialogs() -> None:
    """Ищет диалоги в режиме bot, которые молчат >24ч после последнего сообщения клиента.

    TODO: реально отправлять напоминания через клиентского бота.
          Пока — лог и пометка в facts, чтобы админ видел.
    """
    now = now_utc()
    cutoff_24h = now - timedelta(hours=24)
    cutoff_7d = now - timedelta(days=7)

    async with session_scope() as session:
        result = await session.execute(
            select(Dialog).where(
                Dialog.mode == DialogMode.BOT,
                Dialog.last_activity_at < cutoff_24h,
                Dialog.last_activity_at > cutoff_7d,
            )
        )
        dialogs = result.scalars().all()

    for d in dialogs:
        log.info("followup_candidate", dialog_id=d.id, stage=d.current_stage.value)
