"""Mini App: согласие на обработку ПД + анкета ребёнка."""
from __future__ import annotations

from pathlib import Path

from fastapi import APIRouter, Form, HTTPException, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy import select

from app.common.clock import now_utc
from app.common.errors import DomainError
from app.common.logger import get_logger
from app.db.models.client import Client
from app.db.session import session_scope
from app.miniapp.validate import verify_init_data

router = APIRouter()
log = get_logger(__name__)

BASE_DIR = Path(__file__).resolve().parent
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))

CURRENT_PD_VERSION = "1.0"


@router.get("/consent", response_class=HTMLResponse)
async def consent_page(request: Request) -> HTMLResponse:
    return templates.TemplateResponse(
        request=request,
        name="consent.html",
        context={"version": CURRENT_PD_VERSION},
    )


@router.post("/consent/accept")
async def consent_accept(
    request: Request, init_data: str = Form(alias="initData")
) -> JSONResponse:
    try:
        data = verify_init_data(init_data)
    except DomainError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    tg_user = data.get("user") or {}
    tg_user_id = tg_user.get("id")
    if not tg_user_id:
        raise HTTPException(status_code=400, detail="no user id")

    async with session_scope() as session:
        result = await session.execute(select(Client).where(Client.tg_user_id == tg_user_id))
        client = result.scalar_one_or_none()
        if client is None:
            raise HTTPException(status_code=404, detail="client not found")

        client.pd_consent_at = now_utc()
        client.pd_consent_version = CURRENT_PD_VERSION
        log.info("pd_consent_accepted", client_id=client.id, version=CURRENT_PD_VERSION)

    return JSONResponse({"ok": True})


@router.get("/anketa", response_class=HTMLResponse)
async def anketa_page(request: Request) -> HTMLResponse:
    return templates.TemplateResponse(
        request=request,
        name="anketa.html",
        context={},
    )


@router.post("/anketa/submit")
async def anketa_submit(request: Request) -> JSONResponse:
    payload = await request.json()
    init_data = payload.get("initData", "")
    answers = payload.get("answers", {})

    try:
        data = verify_init_data(init_data)
    except DomainError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    # TODO: сохранить Anketa в БД под child_id из context родительского диалога
    log.info(
        "anketa_submitted",
        tg_user_id=(data.get("user") or {}).get("id"),
        fields=len(answers),
    )
    return JSONResponse({"ok": True})
