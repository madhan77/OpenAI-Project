"""Command-line demo for the Call Center Agent application."""

import argparse
from typing import List

from .center import CallCenter, RoutingError
from .models import Agent, AgentStatus, Interaction, InteractionChannel, Queue, Role


def build_demo_center() -> CallCenter:
    center = CallCenter()
    center.register_agent(
        Agent(
            agent_id="a-100",
            name="Alex",
            role=Role.AGENT,
            skills={"voice", "billing"},
            status=AgentStatus.AVAILABLE,
        )
    )
    center.register_agent(
        Agent(
            agent_id="a-200",
            name="Sam",
            role=Role.AGENT,
            skills={"chat", "technical"},
            status=AgentStatus.AVAILABLE,
        )
    )
    center.register_agent(
        Agent(
            agent_id="sup-1",
            name="Jamie",
            role=Role.SUPERVISOR,
            skills={"voice", "billing"},
            status=AgentStatus.OFFLINE,
        )
    )

    voice_queue = Queue(name="voice_support", skills={"voice"}, priority=1)
    chat_queue = Queue(name="chat_support", skills={"chat"}, priority=2)
    center.create_queue(voice_queue)
    center.create_queue(chat_queue)
    return center


def seed_interactions(center: CallCenter) -> None:
    interactions: List[Interaction] = [
        Interaction(
            interaction_id="call-001",
            channel=InteractionChannel.VOICE,
            customer_name="Jordan",
            required_skills={"voice"},
            priority=1,
            context={"crm_case": "C-1234", "reason": "billing"},
        ),
        Interaction(
            interaction_id="chat-001",
            channel=InteractionChannel.CHAT,
            customer_name="Pat",
            required_skills={"chat"},
            priority=2,
            context={"crm_ticket": "T-4821", "reason": "technical"},
        ),
        Interaction(
            interaction_id="chat-002",
            channel=InteractionChannel.CHAT,
            customer_name="Skyler",
            required_skills={"chat"},
            priority=2,
            context={"crm_ticket": "T-4822", "reason": "order"},
        ),
    ]
    center.receive_interaction("voice_support", interactions[0])
    center.receive_interaction("chat_support", interactions[1])
    center.receive_interaction("chat_support", interactions[2])


def run_demo() -> None:
    center = build_demo_center()
    seed_interactions(center)

    try:
        interaction, agent = center.route_next_interaction()
        print(
            f"Assigned {interaction.interaction_id} ({interaction.channel.value}) to {agent.name}"
        )
        center.complete_interaction(
            agent.agent_id, interaction.interaction_id, wrap_up_code="resolved"
        )
        center.finalize_wrap_up(agent.agent_id)

        first_chat, first_chat_agent = center.route_next_interaction()
        print(
            f"Assigned {first_chat.interaction_id} ({first_chat.channel.value}) to {first_chat_agent.name}"
        )

        second_chat, second_chat_agent = center.route_next_interaction()
        print(
            f"Assigned {second_chat.interaction_id} ({second_chat.channel.value}) to {second_chat_agent.name}"
        )

        center.complete_interaction(
            first_chat_agent.agent_id,
            first_chat.interaction_id,
            wrap_up_code="chat_followup",
        )
        center.complete_interaction(
            second_chat_agent.agent_id,
            second_chat.interaction_id,
            wrap_up_code="chat_resolved",
        )
        if first_chat_agent.agent_id != second_chat_agent.agent_id:
            center.finalize_wrap_up(first_chat_agent.agent_id)
        center.finalize_wrap_up(second_chat_agent.agent_id)
    except RoutingError as exc:
        print(f"Routing error: {exc}")

    dashboard = center.get_supervisor_dashboard()
    print("\nSupervisor dashboard snapshot:")
    for queue_name, metrics in dashboard["queues"].items():
        print(f"  Queue {queue_name}: pending={metrics['pending']} oldest_wait={metrics['oldest_wait_seconds']}s")
    print(f"  Agent statuses: {dashboard['agents']}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Call Center Agent demo")
    parser.parse_args()
    run_demo()
