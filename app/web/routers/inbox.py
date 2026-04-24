"""Список чатов с клиентами + экран одного диалога."""
from __future__ import annotations

from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from app.db.models.admin import Admin
from app.web.auth import current_admin

router = APIRouter()
templates = Jinja2Templates(directory="app/web/templates")


@router.get("", response_class=HTMLResponse)
async def inbox_list(request: Request, admin: Admin = Depends(current_admin)) -> HTMLResponse:
    # TODO: выбор диалогов по фильтру query params
    return templates.TemplateResponse(
        request=request,
        name="inbox_list.html",
        context={"admin": admin, "active_nav": "inbox", "dialogs": []},
    )


@router.get("/{dialog_id}", response_class=HTMLResponse)
async def inbox_detail(
    dialog_id: int, request: Request, admin: Admin = Depends(current_admin)
) -> HTMLResponse:
    # TODO: загрузить диалог, сообщения, карточку клиента
    return templates.TemplateResponse(
        request=request,
        name="inbox_detail.html",
        context={
            "admin": admin,
            "active_nav": "inbox",
            "dialog_id": dialog_id,
            "messages": [],
        },
    )
