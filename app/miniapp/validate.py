"""Валидация Telegram Web App initData.

https://core.telegram.org/bots/webapps#validating-data-received-via-the-mini-app
"""
from __future__ import annotations

import hashlib
import hmac
import json
import time
from typing import Any
from urllib.parse import parse_qsl

from app.common.config import get_settings
from app.common.errors import DomainError

_MAX_AGE_SEC = 86400  # одно суточное окно


def parse_init_data(init_data: str) -> dict[str, str]:
    return dict(parse_qsl(init_data, keep_blank_values=True))


def verify_init_data(init_data: str) -> dict[str, Any]:
    """Проверить подпись initData и вернуть словарь с полями (user декодирован из JSON).

    Raises:
        DomainError: если подпись не прошла или данные просрочены.
    """
    parsed = parse_init_data(init_data)
    auth_hash = parsed.pop("hash", None)
    if not auth_hash:
        raise DomainError("no hash in initData")

    # Только одно из двух токенов — клиентского бота, через который открыли Mini App
    token = get_settings().bot_token_client.get_secret_value()
    if not token:
        raise DomainError("client bot token not configured")

    check_string = "\n".join(f"{k}={v}" for k, v in sorted(parsed.items()))
    secret = hmac.new(b"WebAppData", token.encode(), hashlib.sha256).digest()
    computed = hmac.new(secret, check_string.encode(), hashlib.sha256).hexdigest()

    if not hmac.compare_digest(computed, auth_hash):
        raise DomainError("initData hash mismatch")

    auth_date = int(parsed.get("auth_date", "0"))
    if time.time() - auth_date > _MAX_AGE_SEC:
        raise DomainError("initData expired")

    data: dict[str, Any] = dict(parsed)
    if "user" in parsed:
        data["user"] = json.loads(parsed["user"])
    return data
