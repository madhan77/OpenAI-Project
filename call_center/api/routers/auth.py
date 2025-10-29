from __future__ import annotations

from typing import Any, Dict

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel

from ...center import CallCenter
from ...security import AuthenticationError, AuthorizationService
from ..dependencies import get_auth_service, get_call_center


router = APIRouter(prefix="/auth", tags=["auth"])


class FirebaseTokenRequest(BaseModel):
    id_token: str


class FirebaseTokenResponse(BaseModel):
    access_token: str
    token_type: str
    claims: Dict[str, Any]
    agent: Dict[str, Any]


@router.post("/firebase", response_model=FirebaseTokenResponse)
def verify_firebase_token(
    payload: FirebaseTokenRequest,
    call_center: CallCenter = Depends(get_call_center),
    auth_service: AuthorizationService = Depends(get_auth_service),
) -> FirebaseTokenResponse:
    try:
        claims = auth_service.verify_token(payload.id_token)
    except AuthenticationError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(exc)) from exc

    uid = claims.get("uid") or claims.get("sub")
    if not uid:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token missing UID")

    agent = call_center.find_agent_by_uid(uid)
    if agent is None:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Agent not linked to Firebase UID")

    enriched_claims = dict(claims)
    enriched_claims.setdefault("roles", [agent.role.value])
    enriched_claims.setdefault("agent_id", agent.agent_id)

    return FirebaseTokenResponse(
        access_token=payload.id_token,
        token_type="bearer",
        claims=enriched_claims,
        agent=agent.to_dict(),
    )


__all__ = ["router"]
