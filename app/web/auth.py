"""Проверка Telegram Login Widget.

Алгоритм см. https://core.telegram.org/widgets/login#checking-authorization
"""
from __future__ import annotations

import hashlib
import hmac
import time
from typing import Any

from fastapi import HTTPException, Request, status

from app.common.config import get_settings
from app.db.models.admin import Admin
from app.db.session import session_scope
from sqlalchemy import select

_AUTH_MAX_AGE_SEC = 86400  # 24 часа


def verify_tg_auth(data: dict[str, Any]) -> bool:
    """Проверяет подпись данных от Telegram Login Widget.

    Бот-токен используется для HMAC. Секретом является sha256 токена.
    """
    settings = get_settings()
    token = settings.bot_token_admin.get_secret_value() or settings.bot_token_client.get_secret_value()
    if not token:
        return False

    auth_hash = data.get("hash")
    if not auth_hash:
        return False

    check_pairs = [
        f"{k}={v}" for k, v in sorted(data.items()) if k != "hash"
    ]
    check_string = "\n".join(check_pairs)

    secret_key = hashlib.sha256(token.encode()).digest()
    computed = hmac.new(secret_key, check_string.encode(), hashlib.sha256).hexdigest()

    if not hmac.compare_digest(computed, auth_hash):
        return False

    # Данные не старше 24 часов
    auth_date = int(data.get("auth_date", 0))
    if time.time() - auth_date > _AUTH_MAX_AGE_SEC:
        return False

    return True


async def current_admin(request: Request) -> Admin:
    """Dependency: вернуть текущего админа из сессии или 401."""
    admin_id = request.session.get("admin_id")
    if not admin_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="login required")

    async with session_scope() as session:
        result = await session.execute(select(Admin).where(Admin.id == admin_id))
        admin = result.scalar_one_or_none()
        if admin is None or not admin.active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="admin inactive"
            )
        return admin
