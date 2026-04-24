"""Клиенты и дети."""
from __future__ import annotations

from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from app.db.models.admin import Admin
from app.web.auth import current_admin

router = APIRouter()
templates = Jinja2Templates(directory="app/web/templates")


@router.get("", response_class=HTMLResponse)
async def clients_list(request: Request, admin: Admin = Depends(current_admin)) -> HTMLResponse:
    return templates.TemplateResponse(
        request=request,
        name="clients_list.html",
        context={"admin": admin, "active_nav": "clients", "clients": []},
    )


@router.get("/{client_id}", response_class=HTMLResponse)
async def client_card(
    client_id: int, request: Request, admin: Admin = Depends(current_admin)
) -> HTMLResponse:
    return templates.TemplateResponse(
        request=request,
        name="client_card.html",
        context={"admin": admin, "active_nav": "clients", "client_id": client_id},
    )
