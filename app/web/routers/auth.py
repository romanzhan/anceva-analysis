"""Маршруты авторизации администратора через Telegram Login Widget."""
from __future__ import annotations

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy import select

from app.common.config import get_settings
from app.common.logger import get_logger
from app.db.models.admin import Admin
from app.db.session import session_scope
from app.domain.enums import AdminRole
from app.web.auth import verify_tg_auth

router = APIRouter()
log = get_logger(__name__)

templates = Jinja2Templates(directory="app/web/templates")


@router.get("/login", response_class=HTMLResponse)
async def login_page(request: Request) -> HTMLResponse:
    settings = get_settings()
    return templates.TemplateResponse(
        request=request,
        name="login.html",
        context={
            "bot_username": settings.bot_username_admin,
        },
    )


@router.get("/telegram")
async def telegram_callback(request: Request) -> RedirectResponse:
    """Обратный вызов Telegram Login Widget.

    Виджет делает GET на data-auth-url с параметрами id, first_name, last_name,
    username, photo_url, auth_date, hash.
    """
    data = dict(request.query_params)
    if not verify_tg_auth(data):
        log.warning("tg_auth_failed", params=data)
        return RedirectResponse("/auth/login?error=invalid", status_code=302)

    tg_user_id = int(data["id"])

    async with session_scope() as session:
        result = await session.execute(select(Admin).where(Admin.tg_user_id == tg_user_id))
        admin = result.scalar_one_or_none()

        if admin is None:
            # Первый запуск — автоматически создаём owner'а, если ID совпадает с .env
            settings = get_settings()
            if settings.owner_tg_user_id == tg_user_id:
                admin = Admin(
                    tg_user_id=tg_user_id,
                    tg_username=data.get("username"),
                    name=f"{data.get('first_name', '')} {data.get('last_name', '')}".strip()
                    or "Owner",
                    role=AdminRole.OWNER,
                    active=True,
                )
                session.add(admin)
                await session.flush()
                log.info("owner_bootstrapped", admin_id=admin.id)
            else:
                log.warning("tg_auth_not_admin", tg_user_id=tg_user_id)
                return RedirectResponse("/auth/login?error=no_access", status_code=302)

        if not admin.active:
            return RedirectResponse("/auth/login?error=disabled", status_code=302)

        request.session["admin_id"] = admin.id
        request.session["admin_role"] = admin.role.value
        return RedirectResponse("/admin", status_code=302)


@router.get("/logout")
async def logout(request: Request) -> RedirectResponse:
    request.session.clear()
    return RedirectResponse("/auth/login", status_code=302)
