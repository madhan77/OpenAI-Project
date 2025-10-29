"""Core orchestration logic for the Call Center Agent application."""
from __future__ import annotations
from collections import defaultdict, deque
from datetime import datetime
from typing import Deque, Dict, Iterable, List, Optional, Tuple

from .models import (
    Agent,
    AgentStatus,
    Interaction,
    InteractionChannel,
    Queue,
    Recording,
    Role,
    RoutingStrategy,
)


class RoutingError(RuntimeError):
    """Raised when interactions cannot be routed."""


class AuthorizationError(RuntimeError):
    """Raised when a user attempts an action outside of their role."""


class CallCenter:
    """In-memory model of the call center's operational state."""

    def __init__(self) -> None:
        self.agents: Dict[str, Agent] = {}
        self.queues: Dict[str, Queue] = {}
        self.interactions: Dict[str, Interaction] = {}
        self.interaction_assignments: Dict[str, str] = {}
        self.recordings: Dict[str, Recording] = {}
        self.audit_log: Deque[Tuple[datetime, str, Dict[str, str]]] = deque(maxlen=1000)
        self.supervisor_alerts: Deque[str] = deque(maxlen=50)

    # ------------------------------------------------------------------
    # Administrative APIs
    # ------------------------------------------------------------------
    def register_agent(self, agent: Agent) -> None:
        self.agents[agent.agent_id] = agent
        self._audit("agent_registered", agent_id=agent.agent_id, role=agent.role.value)

    def set_agent_status(self, agent_id: str, status: AgentStatus) -> None:
        agent = self._get_agent(agent_id)
        if status == AgentStatus.AVAILABLE:
            if agent.pending_wrap_up:
                raise RoutingError("Agent must complete wrap-up before returning available")
            if agent.has_active_interactions():
                raise RoutingError("Agent must clear active interactions before returning available")
        agent.set_status(status)
        self._audit("agent_status_changed", agent_id=agent.agent_id, status=status.value)

    def update_agent_skills(self, agent_id: str, skills: Iterable[str]) -> None:
        agent = self._get_agent(agent_id)
        agent.skills = set(skills)
        self._audit("agent_skills_updated", agent_id=agent.agent_id)

    def create_queue(self, queue: Queue) -> None:
        self.queues[queue.name] = queue
        self._audit("queue_created", queue=queue.name, priority=str(queue.priority))

    def set_queue_overflow(self, queue_name: str, overflow_queue: str) -> None:
        queue = self._get_queue(queue_name)
        queue.overflow_queue = overflow_queue
        self._audit("queue_overflow_updated", queue=queue.name, overflow=overflow_queue)

    # ------------------------------------------------------------------
    # Interaction lifecycle
    # ------------------------------------------------------------------
    def receive_interaction(self, queue_name: str, interaction: Interaction) -> None:
        queue = self._get_queue(queue_name)
        if not queue.is_open():
            if queue.overflow_queue:
                self.receive_interaction(queue.overflow_queue, interaction)
                return
            raise RoutingError(f"Queue '{queue_name}' is closed")
        queue.enqueue(interaction)
        self.interactions[interaction.interaction_id] = interaction
        self._audit(
            "interaction_received",
            queue=queue_name,
            interaction_id=interaction.interaction_id,
            priority=str(interaction.priority),
        )
        self._check_queue_thresholds(queue)

    def route_next_interaction(
        self, *, strategy: RoutingStrategy = RoutingStrategy.PRIORITY
    ) -> Tuple[Interaction, Agent]:
        queue = self._select_queue()
        if queue is None:
            raise RoutingError("No interactions available for routing")

        interaction = self._select_interaction(queue, strategy)
        agent = self._select_agent_for_interaction(interaction, queue, strategy)

        agent.assign_interaction(interaction)
        self.interaction_assignments[interaction.interaction_id] = agent.agent_id
        self.recordings[interaction.interaction_id] = Recording(
            interaction_id=interaction.interaction_id, started_at=datetime.utcnow()
        )

        self._audit(
            "interaction_assigned",
            interaction_id=interaction.interaction_id,
            agent_id=agent.agent_id,
            queue=queue.name,
            strategy=strategy.value,
        )
        return interaction, agent

    def transfer_interaction(
        self,
        from_agent_id: str,
        interaction_id: str,
        target: str,
        *,
        notes: Optional[str] = None,
        warm_transfer: bool = True,
    ) -> None:
        agent = self._get_agent(from_agent_id)
        if self.interaction_assignments.get(interaction_id) != agent.agent_id:
            raise RoutingError("Agent has no active interaction matching identifier")

        interaction = self.interactions.get(interaction_id)
        if interaction is None:
            raise RoutingError("Unknown interaction to transfer")

        if notes:
            interaction.add_note(f"Transfer note: {notes}")

        if target in self.agents:
            target_agent = self._get_agent(target)
            if not target_agent.can_accept(interaction):
                raise RoutingError("Target agent is not available for transfer")

            agent.release_interaction(interaction)
            agent.pending_wrap_up.setdefault(
                interaction.interaction_id, notes or "transfer"
            )
            target_agent.assign_interaction(interaction)
            self.interaction_assignments[interaction.interaction_id] = target_agent.agent_id

            if not warm_transfer:
                interaction.add_note("Cold transfer executed")

            if agent.pending_wrap_up and not agent.has_active_interactions():
                agent.set_status(AgentStatus.WRAP_UP)
            elif agent.has_active_interactions():
                agent.set_status(AgentStatus.ON_CALL)
            else:
                agent.set_status(AgentStatus.AVAILABLE)

            self._audit(
                "interaction_transferred_agent",
                from_agent=agent.agent_id,
                to_agent=target_agent.agent_id,
                interaction_id=interaction.interaction_id,
                warm=str(warm_transfer),
            )
        else:
            queue = self._get_queue(target)
            queue.enqueue(interaction)

            agent.release_interaction(interaction)
            agent.pending_wrap_up.setdefault(
                interaction.interaction_id, notes or "transfer"
            )
            self.interaction_assignments.pop(interaction.interaction_id, None)

            if agent.pending_wrap_up:
                agent.set_status(AgentStatus.WRAP_UP)
            elif agent.has_active_interactions():
                agent.set_status(AgentStatus.ON_CALL)
            else:
                agent.set_status(AgentStatus.AVAILABLE)

            self._audit(
                "interaction_transferred_queue",
                from_agent=agent.agent_id,
                to_queue=queue.name,
                interaction_id=interaction.interaction_id,
            )

    def complete_interaction(
        self, agent_id: str, interaction_id: str, wrap_up_code: str
    ) -> None:
        agent = self._get_agent(agent_id)
        if self.interaction_assignments.get(interaction_id) != agent.agent_id:
            raise RoutingError("Agent has no active interaction to complete")

        interaction = self.interactions.get(interaction_id)
        if interaction is None:
            raise RoutingError("Unknown interaction to complete")

        interaction.wrap_up_code = wrap_up_code
        agent.pending_wrap_up[interaction_id] = wrap_up_code

        agent.release_interaction(interaction)
        self.interaction_assignments.pop(interaction_id, None)

        if agent.has_active_interactions():
            agent.set_status(AgentStatus.ON_CALL)
        else:
            agent.set_status(AgentStatus.WRAP_UP)

        recording = self.recordings.get(interaction_id)
        if recording:
            recording.close()

        self._audit(
            "interaction_completed",
            interaction_id=interaction_id,
            agent_id=agent.agent_id,
            wrap_up_code=wrap_up_code,
        )

    def finalize_wrap_up(self, agent_id: str, interaction_id: Optional[str] = None) -> None:
        agent = self._get_agent(agent_id)
        if not agent.pending_wrap_up:
            raise RoutingError("No wrap-up pending for agent")

        if interaction_id is None:
            agent.pending_wrap_up.clear()
        else:
            try:
                agent.pending_wrap_up.pop(interaction_id)
            except KeyError as exc:
                raise RoutingError("Wrap-up not pending for interaction") from exc

        if agent.pending_wrap_up:
            if agent.has_active_interactions():
                agent.set_status(AgentStatus.ON_CALL)
            else:
                agent.set_status(AgentStatus.WRAP_UP)
        elif agent.has_active_interactions():
            agent.set_status(AgentStatus.ON_CALL)
        else:
            agent.set_status(AgentStatus.AVAILABLE)

        self._audit(
            "agent_wrap_up_finalized",
            agent_id=agent.agent_id,
            interaction_id=interaction_id or "all",
        )

    # ------------------------------------------------------------------
    # Supervisor utilities
    # ------------------------------------------------------------------
    def get_supervisor_dashboard(self) -> Dict[str, Dict[str, int]]:
        queue_metrics = {
            name: {
                "pending": len(queue.interactions),
                "oldest_wait_seconds": self._oldest_wait_seconds(queue),
            }
            for name, queue in self.queues.items()
        }

        agent_status_counts = defaultdict(int)
        for agent in self.agents.values():
            agent_status_counts[agent.status.value] += 1

        alerts = list(self.supervisor_alerts)
        return {
            "queues": queue_metrics,
            "agents": dict(agent_status_counts),
            "alerts": {str(i): alert for i, alert in enumerate(alerts, start=1)},
        }

    def schedule_report(self, supervisor_id: str, report_name: str, cadence: str) -> None:
        supervisor = self._get_agent(supervisor_id)
        if supervisor.role not in {Role.SUPERVISOR, Role.ADMIN}:
            raise AuthorizationError("Only supervisors and administrators may schedule reports")
        self._audit(
            "report_scheduled",
            supervisor=supervisor.agent_id,
            report=report_name,
            cadence=cadence,
        )

    def redact_recording(self, qa_agent_id: str, interaction_id: str, description: str) -> None:
        qa_agent = self._get_agent(qa_agent_id)
        if qa_agent.role not in {Role.QA, Role.ADMIN}:
            raise AuthorizationError("Only QA analysts or admins may redact recordings")
        recording = self.recordings.get(interaction_id)
        if recording is None:
            raise RoutingError("Recording not found for interaction")
        recording.add_redaction(description)
        self._audit(
            "recording_redacted", qa_agent=qa_agent.agent_id, interaction_id=interaction_id
        )

    # ------------------------------------------------------------------
    # Analytics helpers
    # ------------------------------------------------------------------
    def compute_average_handle_time(self) -> Optional[float]:
        durations: List[float] = []
        for recording in self.recordings.values():
            if recording.ended_at is None:
                continue
            durations.append((recording.ended_at - recording.started_at).total_seconds())
        if not durations:
            return None
        return sum(durations) / len(durations)

    def compute_agent_utilization(self) -> Dict[str, float]:
        utilization: Dict[str, float] = {}
        for agent in self.agents.values():
            if agent.active_voice_interaction_id:
                utilization[agent.agent_id] = 1.0
            elif agent.active_chat_interactions:
                utilization[agent.agent_id] = (
                    len(agent.active_chat_interactions) / max(agent.max_chat_concurrency, 1)
                )
            else:
                utilization[agent.agent_id] = 0.0
        return utilization

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------
    def _get_agent(self, agent_id: str) -> Agent:
        try:
            return self.agents[agent_id]
        except KeyError as exc:
            raise RoutingError(f"Unknown agent '{agent_id}'") from exc

    def _get_queue(self, queue_name: str) -> Queue:
        try:
            return self.queues[queue_name]
        except KeyError as exc:
            raise RoutingError(f"Unknown queue '{queue_name}'") from exc

    def _select_queue(self) -> Optional[Queue]:
        open_queues = [queue for queue in self.queues.values() if queue.interactions]
        if not open_queues:
            return None
        # Prioritize queues with higher priority (lower number) and longest waiters
        open_queues.sort(key=lambda q: (q.priority, q.peek().created_at))
        return open_queues[0]

    def _select_interaction(
        self, queue: Queue, strategy: RoutingStrategy
    ) -> Interaction:
        interaction = queue.dequeue()
        if interaction is None:
            raise RoutingError("Queue contained no interactions to route")
        return interaction

    def _select_agent_for_interaction(
        self, interaction: Interaction, queue: Queue, strategy: RoutingStrategy
    ) -> Agent:
        eligible_agents = [
            agent
            for agent in self.agents.values()
            if agent.can_accept(interaction)
            and interaction.required_skills <= agent.skills
        ]
        if not eligible_agents:
            raise RoutingError("No eligible agents available")

        if strategy == RoutingStrategy.ROUND_ROBIN:
            ordered_agents = sorted(eligible_agents, key=lambda a: a.agent_id)
            if not ordered_agents:
                raise RoutingError("No agents available for round robin")
            queue.next_agent_index %= len(ordered_agents)
            agent = ordered_agents[queue.next_agent_index]
            queue.next_agent_index = (queue.next_agent_index + 1) % len(ordered_agents)
            return agent

        if strategy == RoutingStrategy.LONGEST_IDLE:
            return min(eligible_agents, key=lambda a: a.last_status_change)

        if strategy == RoutingStrategy.PRIORITY:
            return min(
                eligible_agents,
                key=lambda a: (
                    len(a.active_chat_interactions)
                    if interaction.channel == InteractionChannel.CHAT
                    else 0,
                    -len(a.skills & interaction.required_skills),
                    a.last_status_change,
                ),
            )

        raise RoutingError(f"Unsupported routing strategy: {strategy}")

    def _oldest_wait_seconds(self, queue: Queue) -> int:
        oldest = queue.peek()
        if oldest is None:
            return 0
        return int((datetime.utcnow() - oldest.created_at).total_seconds())

    def _check_queue_thresholds(self, queue: Queue) -> None:
        if queue.max_wait_seconds is None or not queue.interactions:
            return
        oldest_wait = self._oldest_wait_seconds(queue)
        if oldest_wait > queue.max_wait_seconds:
            message = (
                f"Queue {queue.name} wait time {oldest_wait}s exceeded threshold "
                f"{queue.max_wait_seconds}s"
            )
            self.supervisor_alerts.appendleft(message)

    def _audit(self, event: str, **data: str) -> None:
        self.audit_log.append((datetime.utcnow(), event, data))
