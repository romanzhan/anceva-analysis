"""Dashboard — главный экран админки."""
from __future__ import annotations

from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from app.db.models.admin import Admin
from app.web.auth import current_admin

router = APIRouter()
templates = Jinja2Templates(directory="app/web/templates")


@router.get("", response_class=HTMLResponse)
async def dashboard(
    request: Request,
    admin: Admin = Depends(current_admin),
) -> HTMLResponse:
    # TODO: запросы в БД — считаем KPI за сегодня
    kpis = {
        "new_today": 0,
        "in_progress": 0,
        "di_tomorrow": 0,
        "escalations": 0,
    }
    return templates.TemplateResponse(
        request=request,
        name="dashboard.html",
        context={"admin": admin, "kpis": kpis, "active_nav": "dashboard"},
    )
