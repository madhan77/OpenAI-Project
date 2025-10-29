from __future__ import annotations

from typing import List

from fastapi import APIRouter, Depends, HTTPException, status

from ...center import CallCenter, RoutingError
from ...models import Agent, AgentStatus, Role
from ...security import AuthorizationService
from ..dependencies import authorize, get_auth_service, get_call_center


router = APIRouter(prefix="/agents", tags=["agents"])


@router.post("", status_code=status.HTTP_201_CREATED)
def create_agent(
    agent: Agent,
    call_center: CallCenter = Depends(get_call_center),
    authz: dict = Depends(authorize),
) -> Agent:
    _require_role(authz, {Role.ADMIN.value})
    call_center.register_agent(agent)
    return agent


@router.get("", response_model=List[Agent])
def list_agents(
    call_center: CallCenter = Depends(get_call_center),
    authz: dict = Depends(authorize),
) -> List[Agent]:
    _require_role(authz, {Role.ADMIN.value, Role.SUPERVISOR.value})
    return list(call_center.agents.values())


@router.post("/{agent_id}/status")
def update_status(
    agent_id: str,
    status_payload: AgentStatus,
    call_center: CallCenter = Depends(get_call_center),
    authz: dict = Depends(authorize),
) -> Agent:
    if authz["sub"] != agent_id and Role.SUPERVISOR.value not in authz["roles"]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions")
    try:
        call_center.set_agent_status(agent_id, status_payload)
    except RoutingError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc
    return call_center.agents[agent_id]


@router.post("/{agent_id}/skills")
def update_skills(
    agent_id: str,
    skills: List[str],
    call_center: CallCenter = Depends(get_call_center),
    authz: dict = Depends(authorize),
) -> Agent:
    if Role.ADMIN.value not in authz["roles"]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions")
    call_center.update_agent_skills(agent_id, skills)
    return call_center.agents[agent_id]


@router.post("/{agent_id}/password")
def set_password(
    agent_id: str,
    payload: dict,
    call_center: CallCenter = Depends(get_call_center),
    auth_service: AuthorizationService = Depends(get_auth_service),
    authz: dict = Depends(authorize),
) -> dict:
    _require_role(authz, {Role.ADMIN.value, Role.SUPERVISOR.value})
    agent = call_center.agents.get(agent_id)
    if not agent:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Agent not found")
    password = payload.get("password")
    if not password:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Password required")
    agent.password_hash = auth_service.hash_password(password)
    return {"status": "ok"}


def _require_role(authz: dict, roles: set[str]) -> None:
    if roles.isdisjoint(set(authz.get("roles", []))):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions")


__all__ = ["router"]

