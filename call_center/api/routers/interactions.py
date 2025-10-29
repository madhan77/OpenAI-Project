from __future__ import annotations

from typing import List

from fastapi import APIRouter, Depends, HTTPException, status

from ...center import CallCenter, RoutingError
from ...models import Interaction, Role, RoutingStrategy
from ...metrics import interaction_counter, queue_depth_gauge
from ..dependencies import authorize, get_call_center


router = APIRouter(prefix="/interactions", tags=["interactions"])


@router.post("", status_code=status.HTTP_202_ACCEPTED)
def enqueue_interaction(
    queue: str,
    interaction: Interaction,
    call_center: CallCenter = Depends(get_call_center),
    authz: dict = Depends(authorize),
) -> dict:
    if Role.AGENT.value not in authz["roles"] and Role.SUPERVISOR.value not in authz["roles"]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions")
    try:
        call_center.receive_interaction(queue, interaction)
    except RoutingError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc
    queue_depth_gauge.labels(queue=queue).set(len(call_center.queues[queue].interactions))
    return {"status": "queued", "interaction_id": interaction.interaction_id}


@router.post("/route")
def route_next(
    strategy: RoutingStrategy = RoutingStrategy.PRIORITY,
    call_center: CallCenter = Depends(get_call_center),
    authz: dict = Depends(authorize),
) -> dict:
    if Role.SUPERVISOR.value not in authz["roles"] and Role.ADMIN.value not in authz["roles"]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions")
    try:
        interaction, agent = call_center.route_next_interaction(strategy=strategy)
    except RoutingError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    interaction_counter.labels(channel=interaction.channel.value, status="assigned").inc()
    return {"interaction": interaction, "agent": agent}


@router.get("", response_model=List[Interaction])
def list_interactions(
    call_center: CallCenter = Depends(get_call_center),
    authz: dict = Depends(authorize),
) -> List[Interaction]:
    if Role.SUPERVISOR.value not in authz["roles"]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions")
    return list(call_center.interactions.values())


__all__ = ["router"]

