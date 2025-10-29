"""FastAPI dependency wiring."""
from __future__ import annotations

from functools import lru_cache

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from ..center import CallCenter
from ..config import get_config
from ..security import AuthenticationError, AuthorizationService


http_bearer = HTTPBearer(auto_error=False)


@lru_cache(maxsize=1)
def get_call_center() -> CallCenter:
    return CallCenter()


@lru_cache(maxsize=1)
def get_auth_service() -> AuthorizationService:
    return AuthorizationService()


def authorize(
    credentials: HTTPAuthorizationCredentials = Depends(http_bearer),
    call_center: CallCenter = Depends(get_call_center),
) -> dict:
    if credentials is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing bearer token")

    service = get_auth_service()
    try:
        claims = service.verify_token(credentials.credentials)
    except AuthenticationError as exc:  # pragma: no cover - defensive branch
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(exc)) from exc

    uid = claims.get("uid") or claims.get("sub")
    if not uid:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token missing UID")

    agent = call_center.find_agent_by_uid(uid)
    if agent is None:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Agent not linked to Firebase UID")

    enriched = dict(claims)
    enriched["sub"] = agent.agent_id
    enriched.setdefault("roles", [agent.role.value])
    enriched["agent_id"] = agent.agent_id
    return enriched


def get_settings():
    return get_config()


__all__ = ["authorize", "get_auth_service", "get_call_center", "get_settings"]

