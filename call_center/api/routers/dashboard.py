from __future__ import annotations

from datetime import datetime
from typing import Any, Dict

from fastapi import APIRouter, Depends, HTTPException, status

from ...center import CallCenter
from ...models import Role
from ...metrics import active_agents_gauge, queue_depth_gauge
from ..dependencies import authorize, get_call_center


router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("/summary")
def get_summary(
    call_center: CallCenter = Depends(get_call_center),
    authz: dict = Depends(authorize),
) -> Dict[str, Any]:
    if Role.SUPERVISOR.value not in authz["roles"] and Role.ADMIN.value not in authz["roles"]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions")
    agents = list(call_center.agents.values())
    queues = list(call_center.queues.values())
    status_counts: dict[str, int] = {}
    for agent in agents:
        status_counts[agent.status.value] = status_counts.get(agent.status.value, 0) + 1
    for status, count in status_counts.items():
        active_agents_gauge.labels(status=status).set(count)
    for queue in queues:
        queue_depth_gauge.labels(queue=queue.name).set(queue.size)
    return {
        "generated_at": datetime.utcnow().isoformat(),
        "agents": [agent.to_dict() for agent in agents],
        "queues": [queue.to_dict() for queue in queues],
        "interactions": [interaction.to_dict() for interaction in call_center.interactions.values()],
    }


__all__ = ["router"]

