"""Tests for the Call Center Agent application."""
from datetime import datetime, timedelta

import pytest

from call_center.center import AuthorizationError, CallCenter, RoutingError
from call_center.models import (
    Agent,
    AgentStatus,
    Interaction,
    InteractionChannel,
    Queue,
    Role,
    RoutingStrategy,
)


@pytest.fixture()
def center() -> CallCenter:
    center = CallCenter()
    center.create_queue(Queue(name="priority", skills={"voice"}, priority=1))
    center.create_queue(Queue(name="standard", skills={"chat"}, priority=2))

    center.register_agent(
        Agent(
            agent_id="ag-1",
            name="Avery",
            role=Role.AGENT,
            skills={"voice", "chat"},
            status=AgentStatus.AVAILABLE,
        )
    )
    center.register_agent(
        Agent(
            agent_id="sup-1",
            name="Morgan",
            role=Role.SUPERVISOR,
            skills={"voice", "chat"},
            status=AgentStatus.AVAILABLE,
        )
    )
    center.register_agent(
        Agent(
            agent_id="qa-1",
            name="Riley",
            role=Role.QA,
            skills={"voice"},
            status=AgentStatus.AVAILABLE,
        )
    )
    return center


def test_priority_queue_selected(center: CallCenter) -> None:
    voice_interaction = Interaction(
        interaction_id="call-1",
        channel=InteractionChannel.VOICE,
        customer_name="Customer A",
        required_skills={"voice"},
        priority=1,
    )
    chat_interaction = Interaction(
        interaction_id="chat-1",
        channel=InteractionChannel.CHAT,
        customer_name="Customer B",
        required_skills={"chat"},
        priority=5,
    )

    center.receive_interaction("standard", chat_interaction)
    center.receive_interaction("priority", voice_interaction)

    interaction, agent = center.route_next_interaction(strategy=RoutingStrategy.PRIORITY)
    assert interaction.interaction_id == "call-1"
    assert agent.agent_id == "ag-1"


def test_wrap_up_required_before_available(center: CallCenter) -> None:
    interaction = Interaction(
        interaction_id="call-2",
        channel=InteractionChannel.VOICE,
        customer_name="Customer C",
        required_skills={"voice"},
        priority=1,
    )
    center.receive_interaction("priority", interaction)
    interaction, agent = center.route_next_interaction()
    center.complete_interaction(
        agent.agent_id, interaction.interaction_id, wrap_up_code="resolved"
    )

    with pytest.raises(RoutingError):
        center.set_agent_status(agent.agent_id, AgentStatus.AVAILABLE)

    center.finalize_wrap_up(agent.agent_id)
    assert center.agents[agent.agent_id].status == AgentStatus.AVAILABLE


def test_supervisor_alert_on_wait_threshold(center: CallCenter) -> None:
    queue = center.queues["priority"]
    queue.max_wait_seconds = 60

    interaction = Interaction(
        interaction_id="call-3",
        channel=InteractionChannel.VOICE,
        customer_name="Customer D",
        required_skills={"voice"},
        priority=1,
    )
    # Pretend the interaction has been waiting for two minutes
    interaction.created_at = datetime.utcnow() - timedelta(seconds=120)

    center.receive_interaction("priority", interaction)

    dashboard = center.get_supervisor_dashboard()
    assert dashboard["alerts"], "Expected an alert when wait threshold exceeded"


def test_transfer_to_other_agent(center: CallCenter) -> None:
    second_agent = Agent(
        agent_id="ag-2",
        name="Quinn",
        role=Role.AGENT,
        skills={"voice", "chat"},
        status=AgentStatus.AVAILABLE,
    )
    center.register_agent(second_agent)

    interaction = Interaction(
        interaction_id="call-4",
        channel=InteractionChannel.VOICE,
        customer_name="Customer E",
        required_skills={"voice"},
        priority=1,
    )
    center.receive_interaction("priority", interaction)
    interaction, agent = center.route_next_interaction()

    center.transfer_interaction(
        agent.agent_id, interaction.interaction_id, "ag-2", notes="Escalating"
    )

    assert center.agents["ag-2"].active_voice_interaction_id == "call-4"
    assert center.agents["ag-2"].status == AgentStatus.ON_CALL
    assert center.agents["ag-1"].status == AgentStatus.WRAP_UP


def test_only_supervisor_can_schedule_report(center: CallCenter) -> None:
    with pytest.raises(AuthorizationError):
        center.schedule_report("ag-1", "daily_metrics", cadence="daily")

    center.schedule_report("sup-1", "daily_metrics", cadence="daily")
    assert center.audit_log


def test_qa_can_redact_recording(center: CallCenter) -> None:
    interaction = Interaction(
        interaction_id="call-5",
        channel=InteractionChannel.VOICE,
        customer_name="Customer F",
        required_skills={"voice"},
        priority=1,
    )
    center.receive_interaction("priority", interaction)
    interaction, agent = center.route_next_interaction()
    center.complete_interaction(
        agent.agent_id, interaction.interaction_id, wrap_up_code="billing_issue"
    )
    center.redact_recording("qa-1", "call-5", "Removed credit card number")
    recording = center.recordings["call-5"]
    assert recording.redactions == ["Removed credit card number"]


def test_agent_can_handle_two_chats(center: CallCenter) -> None:
    center.set_agent_status("sup-1", AgentStatus.OFFLINE)

    chat_one = Interaction(
        interaction_id="chat-10",
        channel=InteractionChannel.CHAT,
        customer_name="Customer G",
        required_skills={"chat"},
        priority=1,
    )
    chat_two = Interaction(
        interaction_id="chat-11",
        channel=InteractionChannel.CHAT,
        customer_name="Customer H",
        required_skills={"chat"},
        priority=2,
    )

    center.receive_interaction("standard", chat_one)
    center.receive_interaction("standard", chat_two)

    first_assignment, first_agent = center.route_next_interaction()
    second_assignment, second_agent = center.route_next_interaction()

    assert first_agent.agent_id == "ag-1"
    assert second_agent.agent_id == "ag-1"
    assert {first_assignment.interaction_id, second_assignment.interaction_id} == center.agents[
        "ag-1"
    ].active_chat_interactions

    center.complete_interaction("ag-1", first_assignment.interaction_id, wrap_up_code="resolved")
    assert center.agents["ag-1"].status == AgentStatus.ON_CALL

    center.complete_interaction("ag-1", second_assignment.interaction_id, wrap_up_code="resolved")
    assert center.agents["ag-1"].status == AgentStatus.WRAP_UP

    center.finalize_wrap_up("ag-1")
    assert center.agents["ag-1"].status == AgentStatus.AVAILABLE
