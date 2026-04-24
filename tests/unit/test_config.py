"""Санити на загрузку конфига."""
from __future__ import annotations

from app.common.config import Environment, get_settings


def test_settings_loads() -> None:
    s = get_settings()
    assert s.env in (Environment.LOCAL, Environment.STAGING, Environment.PRODUCTION)
    assert s.database_url
