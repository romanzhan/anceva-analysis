"""Настройки приложения — загружаются из .env + переменных окружения.

Все настройки неизменяемы после запуска. Доступ через `get_settings()` (кэшируется).
"""
from __future__ import annotations

from enum import StrEnum
from functools import lru_cache
from pathlib import Path

from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict

PROJECT_ROOT = Path(__file__).resolve().parents[2]


class Environment(StrEnum):
    LOCAL = "local"
    STAGING = "staging"
    PRODUCTION = "production"


class LogFormat(StrEnum):
    CONSOLE = "console"
    JSON = "json"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=PROJECT_ROOT / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )

    # -- Application ----------------------------------------------------------
    env: Environment = Environment.LOCAL
    log_level: str = "INFO"
    log_format: LogFormat = LogFormat.CONSOLE
    tz: str = "Asia/Qyzylorda"

    # -- Telegram -------------------------------------------------------------
    bot_token_client: SecretStr = SecretStr("")
    bot_token_admin: SecretStr = SecretStr("")
    bot_webhook_url: str = ""
    bot_webhook_secret: SecretStr = SecretStr("")
    bot_username_client: str = "anceva_bot"
    bot_username_admin: str = "anceva_admin_bot"

    # -- LLM ------------------------------------------------------------------
    gemini_api_key: SecretStr = SecretStr("")
    gemini_model_main: str = "gemini-2.0-flash"
    gemini_model_lite: str = "gemini-2.0-flash-lite"
    gemini_model_heavy: str = "gemini-2.5-pro"
    gemini_timeout_sec: int = 30

    # -- Database -------------------------------------------------------------
    database_url: str = "sqlite+aiosqlite:///./var/anceva.sqlite"

    # -- Web ------------------------------------------------------------------
    web_host: str = "0.0.0.0"  # noqa: S104 — контейнер слушает на всех интерфейсах
    web_port: int = 8000
    web_base_url: str = "http://localhost:8000"
    web_session_secret: SecretStr = SecretStr("change-me-in-production")
    miniapp_base_url: str = "http://localhost:8000/app"

    # -- Admins ---------------------------------------------------------------
    owner_tg_user_id: int | None = None

    # -- Kaspi ----------------------------------------------------------------
    # Реальная ссылка вписывается через .env, не хранится в коде.
    kaspi_pay_link: str = ""
    kaspi_merchant_name: str = ""

    # -- Sentry ---------------------------------------------------------------
    sentry_dsn: str = ""
    sentry_traces_sample_rate: float = Field(default=0.1, ge=0.0, le=1.0)

    # -- Feature flags --------------------------------------------------------
    feature_shadow_mode: bool = True
    feature_auto_invoice: bool = False
    feature_kaspi_ocr: bool = False

    # -- Derived --------------------------------------------------------------

    @property
    def is_prod(self) -> bool:
        return self.env == Environment.PRODUCTION

    @property
    def is_webhook_mode(self) -> bool:
        return bool(self.bot_webhook_url)

    @property
    def var_dir(self) -> Path:
        path = PROJECT_ROOT / "var"
        path.mkdir(exist_ok=True)
        return path


@lru_cache
def get_settings() -> Settings:
    """Кэшированный синглтон настроек. Не вызывать на горячем пути."""
    return Settings()
