"""Оплаты: план / факт / просрочка, генерация счетов."""
from __future__ import annotations

from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from app.db.models.admin import Admin
from app.web.auth import current_admin

router = APIRouter()
templates = Jinja2Templates(directory="app/web/templates")


@router.get("", response_class=HTMLResponse)
async def payments_view(request: Request, admin: Admin = Depends(current_admin)) -> HTMLResponse:
    return templates.TemplateResponse(
        request=request,
        name="payments.html",
        context={"admin": admin, "active_nav": "payments"},
    )
