"""FastAPI dependency wiring."""
from __future__ import annotations

from functools import lru_cache

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from ..center import CallCenter
from ..config import get_config
from ..security import AuthenticationError, AuthorizationService


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/token")


@lru_cache(maxsize=1)
def get_call_center() -> CallCenter:
    return CallCenter()


@lru_cache(maxsize=1)
def get_auth_service() -> AuthorizationService:
    return AuthorizationService()


def authorize(token: str = Depends(oauth2_scheme)) -> dict:
    service = get_auth_service()
    try:
        return service.verify_token(token)
    except AuthenticationError as exc:  # pragma: no cover - defensive branch
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(exc)) from exc


def get_settings():
    return get_config()


__all__ = ["authorize", "get_auth_service", "get_call_center", "get_settings"]

