"""UI routes served through FastAPI."""
from __future__ import annotations

from pathlib import Path

from fastapi import APIRouter, FastAPI, Header, HTTPException, Query, Request, status
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from ..api.dependencies import get_auth_service, get_call_center
from ..config import get_config

templates = Jinja2Templates(directory=str(Path(__file__).parent / "templates"))


def register_ui(app: FastAPI) -> None:
    router = APIRouter()

    auth_service = get_auth_service()

    @router.get("/login", response_class=HTMLResponse)
    async def login(request: Request) -> HTMLResponse:
        config = get_config()
        context = {
            "request": request,
            "firebase_project_id": config.firebase_project_id,
            "firebase_api_key": config.firebase_web_api_key,
            "firebase_emulator_mode": config.firebase_emulator_mode,
        }
        return templates.TemplateResponse("login.html", context)

    @router.get("/", response_class=HTMLResponse)
    async def dashboard(
        request: Request,
        token: str | None = Query(default=None),
        authorization: str | None = Header(default=None, alias="Authorization"),
    ) -> HTMLResponse:
        token_value: str | None = None
        if authorization and authorization.lower().startswith("bearer "):
            token_value = authorization.split(" ", 1)[1]
        elif token:
            token_value = token
        if not token_value:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing bearer token")
        authz = auth_service.verify_token(token_value)
        call_center = get_call_center()
        context = {
            "request": request,
            "user": authz,
            "agents": list(call_center.agents.values()),
            "queues": list(call_center.queues.values()),
            "interactions": list(call_center.interactions.values()),
        }
        return templates.TemplateResponse("dashboard.html", context)

    app.include_router(router)


__all__ = ["register_ui"]

