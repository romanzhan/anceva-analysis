"""FastAPI-приложение: админка + Mini App endpoints + webhook клиентского бота.

Маршруты:
  /                   → redirect на /admin (если залогинен) или /auth
  /admin/*            → защищённые страницы админки
  /auth/*             → Telegram Login
  /app/*              → Telegram Mini App (анкета, согласие)
  /api/*              → JSON-эндпоинты для htmx и mini app
  /healthz            → healthcheck для Railway
  /webhook/<secret>   → Telegram webhook (если BOT_WEBHOOK_URL задан)
"""
from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware

from app.common.config import get_settings
from app.common.logger import configure_logging, get_logger
from app.miniapp.router import router as miniapp_router
from app.web.routers import (
    auth,
    broadcasts,
    clients,
    dashboard,
    inbox,
    payments,
    schedule,
    settings as settings_router,
    templates as templates_router,
)

log = get_logger("web")

configure_logging()
_settings = get_settings()

BASE_DIR = Path(__file__).resolve().parent
TEMPLATE_DIR = BASE_DIR / "templates"
STATIC_DIR = BASE_DIR / "static"

templates = Jinja2Templates(directory=str(TEMPLATE_DIR))

app = FastAPI(
    title="Anceva Admin",
    version="0.1.0",
    docs_url="/api/docs" if not _settings.is_prod else None,
    redoc_url=None,
)

app.add_middleware(
    SessionMiddleware,
    secret_key=_settings.web_session_secret.get_secret_value() or "dev-secret-change-me",
    https_only=_settings.is_prod,
    same_site="lax",
)

app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

# Роутеры
app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(dashboard.router, prefix="/admin", tags=["admin"])
app.include_router(inbox.router, prefix="/admin/inbox", tags=["admin"])
app.include_router(clients.router, prefix="/admin/clients", tags=["admin"])
app.include_router(schedule.router, prefix="/admin/schedule", tags=["admin"])
app.include_router(payments.router, prefix="/admin/payments", tags=["admin"])
app.include_router(broadcasts.router, prefix="/admin/broadcasts", tags=["admin"])
app.include_router(templates_router.router, prefix="/admin/templates", tags=["admin"])
app.include_router(settings_router.router, prefix="/admin/settings", tags=["admin"])
app.include_router(miniapp_router, prefix="/app", tags=["miniapp"])


@app.get("/", include_in_schema=False)
async def root(request: Request) -> RedirectResponse:
    target = "/admin" if request.session.get("admin_id") else "/auth/login"
    return RedirectResponse(target, status_code=302)


@app.get("/healthz", include_in_schema=False)
async def healthz() -> dict[str, str]:
    return {"status": "ok"}


@app.exception_handler(404)
async def not_found(request: Request, _exc) -> HTMLResponse:  # type: ignore[no-untyped-def]
    return templates.TemplateResponse(
        request=request, name="404.html", status_code=404
    )
