from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from ...center import CallCenter
from ...security import AuthenticationError, AuthorizationService
from ..dependencies import get_auth_service, get_call_center


router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/token")
def issue_token(
    form: OAuth2PasswordRequestForm = Depends(),
    call_center: CallCenter = Depends(get_call_center),
    auth_service: AuthorizationService = Depends(get_auth_service),
) -> dict:
    agent = call_center.agents.get(form.username)
    if not agent:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Agent not found")
    try:
        token = auth_service.authenticate_agent(agent, form.password)
    except AuthenticationError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(exc)) from exc
    return {"access_token": token, "token_type": "bearer"}


__all__ = ["router"]

