from fastapi.testclient import TestClient

from call_center import Agent, AgentStatus, Queue, Role
from call_center.api.dependencies import get_auth_service, get_call_center
from call_center.api.server import app


ADMIN_UID = "firebase-admin"


def setup_module(_) -> None:
    center = get_call_center()
    if "voice" not in center.queues:
        center.create_queue(Queue(name="voice", skills={"voice"}, priority=1))
    if "admin" not in center.agents:
        center.register_agent(
            Agent(
                agent_id="admin",
                name="Admin",
                role=Role.ADMIN,
                skills={"voice"},
                status=AgentStatus.AVAILABLE,
                firebase_uid=ADMIN_UID,
            )
        )
    else:
        center.agents["admin"].firebase_uid = ADMIN_UID


def _mint_token(agent_id: str) -> str:
    center = get_call_center()
    auth_service = get_auth_service()
    agent = center.agents[agent_id]
    assert agent.firebase_uid, "Agent must have a Firebase UID for tests"
    return auth_service.issue_token(uid=agent.firebase_uid, roles=[agent.role])


def _login(client: TestClient, agent_id: str) -> str:
    token = _mint_token(agent_id)
    response = client.post("/api/auth/firebase", json={"id_token": token})
    assert response.status_code == 200, response.text
    return response.json()["access_token"]


def test_agent_lifecycle_via_api() -> None:
    client = TestClient(app)
    token = _login(client, "admin")

    payload = {
        "agent_id": "agent-1",
        "name": "Avery",
        "role": "agent",
        "skills": ["voice"],
        "status": "available",
    }
    response = client.post("/api/agents", json=payload, headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 201, response.text

    response = client.post(
        "/api/agents/agent-1/identity",
        json={"firebase_uid": "firebase-agent-1"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200, response.text

    agent_token = _login(client, "agent-1")
    response = client.post(
        "/api/agents/agent-1/status",
        json="on_call",
        headers={"Authorization": f"Bearer {agent_token}"},
    )
    assert response.status_code == 200, response.text
    assert response.json()["status"] == "on_call"


def test_interaction_routing_flow() -> None:
    client = TestClient(app)
    token = _login(client, "admin")

    interaction_payload = {
        "interaction_id": "call-123",
        "channel": "voice",
        "customer_name": "Taylor",
        "required_skills": ["voice"],
        "priority": 1,
    }
    response = client.post(
        "/api/interactions?queue=voice",
        json=interaction_payload,
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 202, response.text

    response = client.post(
        "/api/interactions/route",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200, response.text
    body = response.json()
    assert body["interaction"]["interaction_id"] == "call-123"
    assert body["agent"]["agent_id"] in {"admin", "agent-1"}


def test_login_page_serves_firebase_config() -> None:
    client = TestClient(app)
    response = client.get("/login")
    assert response.status_code == 200
    body = response.text
    assert "Call Center Login" in body
    assert "open-ai-project-723a7.firebaseapp.com" in body
    assert "token" in body
