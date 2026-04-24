"""Общие фикстуры pytest."""
from __future__ import annotations

import os

import pytest

os.environ.setdefault("ENV", "local")
os.environ.setdefault("DATABASE_URL", "sqlite+aiosqlite:///:memory:")
os.environ.setdefault("WEB_SESSION_SECRET", "test-secret")


@pytest.fixture(scope="session")
def anyio_backend() -> str:
    return "asyncio"
