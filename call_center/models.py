"""Domain models for the Call Center Agent application."""
from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime, time
from enum import Enum
from typing import Dict, List, Optional, Sequence, Set


class Role(str, Enum):
    """Role-based access control roles supported by the system."""

    AGENT = "agent"
    SUPERVISOR = "supervisor"
    ADMIN = "administrator"
    QA = "qa"


class AgentStatus(str, Enum):
    """Lifecycle states for an agent."""

    AVAILABLE = "available"
    ON_CALL = "on_call"
    WRAP_UP = "wrap_up"
    OFFLINE = "offline"


class InteractionChannel(str, Enum):
    """Supported interaction channels for the MVP."""

    VOICE = "voice"
    CHAT = "chat"


class RoutingStrategy(str, Enum):
    """Supported routing strategies defined in the PRD."""

    ROUND_ROBIN = "round_robin"
    LONGEST_IDLE = "longest_idle"
    PRIORITY = "priority"


@dataclass
class Agent:
    """Represents a contact center agent."""

    agent_id: str
    name: str
    role: Role
    skills: Set[str] = field(default_factory=set)
    status: AgentStatus = AgentStatus.OFFLINE
    last_status_change: datetime = field(default_factory=datetime.utcnow)
    active_voice_interaction_id: Optional[str] = None
    active_chat_interactions: Set[str] = field(default_factory=set)
    pending_wrap_up: Dict[str, str] = field(default_factory=dict)
    max_chat_concurrency: int = 2

    password_hash: Optional[str] = None

    def set_status(self, status: AgentStatus) -> None:
        self.status = status
        self.last_status_change = datetime.utcnow()

    # ------------------------------------------------------------------
    # Interaction helpers
    # ------------------------------------------------------------------
    def can_accept(self, interaction: "Interaction") -> bool:
        """Return True if the agent can accept the provided interaction."""

        if self.status == AgentStatus.OFFLINE:
            return False

        if self.pending_wrap_up:
            return False

        if interaction.channel == InteractionChannel.VOICE:
            return (
                self.status == AgentStatus.AVAILABLE
                and self.active_voice_interaction_id is None
            )

        if interaction.channel == InteractionChannel.CHAT:
            if self.status not in {AgentStatus.AVAILABLE, AgentStatus.ON_CALL}:
                return False
            return len(self.active_chat_interactions) < self.max_chat_concurrency

        return False

    def assign_interaction(self, interaction: "Interaction") -> None:
        """Mark the agent as handling the provided interaction."""

        if interaction.channel == InteractionChannel.VOICE:
            self.active_voice_interaction_id = interaction.interaction_id
        else:
            self.active_chat_interactions.add(interaction.interaction_id)

        if self.status != AgentStatus.ON_CALL:
            self.set_status(AgentStatus.ON_CALL)

    def release_interaction(self, interaction: "Interaction") -> None:
        """Remove the interaction from the agent's active assignments."""

        if interaction.channel == InteractionChannel.VOICE:
            if self.active_voice_interaction_id == interaction.interaction_id:
                self.active_voice_interaction_id = None
        else:
            self.active_chat_interactions.discard(interaction.interaction_id)

    def has_active_interactions(self) -> bool:
        """Return True when the agent is handling any interactions."""

        return bool(self.active_voice_interaction_id or self.active_chat_interactions)

    def to_dict(self) -> dict[str, object]:
        return {
            "agent_id": self.agent_id,
            "display_name": self.name,
            "role": self.role.value,
            "skills": sorted(self.skills),
            "status": self.status.value,
            "last_status_change": self.last_status_change.isoformat(),
        }


@dataclass(order=True)
class Interaction:
    """Represents an interaction waiting to be handled."""

    sort_index: int = field(init=False, repr=False)
    interaction_id: str
    channel: InteractionChannel
    customer_name: str
    required_skills: Set[str]
    priority: int
    created_at: datetime = field(default_factory=datetime.utcnow)
    context: Dict[str, str] = field(default_factory=dict)
    notes: List[str] = field(default_factory=list)
    wrap_up_code: Optional[str] = None

    def __post_init__(self) -> None:
        # Lower numbers indicate higher priority for the queue ordering
        self.sort_index = self.priority

    def add_note(self, note: str) -> None:
        timestamp = datetime.utcnow().isoformat(timespec="seconds")
        self.notes.append(f"[{timestamp}] {note}")

    def to_dict(self) -> dict[str, object]:
        return {
            "interaction_id": self.interaction_id,
            "channel": self.channel.value,
            "customer_name": self.customer_name,
            "required_skills": sorted(self.required_skills),
            "priority": self.priority,
            "created_at": self.created_at.isoformat(),
            "notes": list(self.notes),
            "wrap_up_code": self.wrap_up_code,
        }


@dataclass
class BusinessHours:
    """Represents business hours for routing policies."""

    days: Set[int]
    open_time: time
    close_time: time

    def is_open(self, timestamp: Optional[datetime] = None) -> bool:
        check_time = timestamp or datetime.utcnow()
        return (
            check_time.weekday() in self.days
            and self.open_time <= check_time.time() <= self.close_time
        )


@dataclass
class Queue:
    """Queue definition with routing metadata."""

    name: str
    skills: Set[str]
    priority: int
    business_hours: Optional[BusinessHours] = None
    overflow_queue: Optional[str] = None
    max_wait_seconds: Optional[int] = None
    ivr_path: Optional[Sequence[str]] = None
    interactions: List[Interaction] = field(default_factory=list)
    next_agent_index: int = 0
    recording_retention_days: int = 60

    def enqueue(self, interaction: Interaction) -> None:
        self.interactions.append(interaction)
        # Keep interactions ordered by priority and created_at
        self.interactions.sort(key=lambda inter: (inter.priority, inter.created_at))

    def dequeue(self) -> Optional[Interaction]:
        if not self.interactions:
            return None
        return self.interactions.pop(0)

    def peek(self) -> Optional[Interaction]:
        if not self.interactions:
            return None
        return self.interactions[0]

    def is_open(self) -> bool:
        if self.business_hours is None:
            return True
        return self.business_hours.is_open()

    def __len__(self) -> int:
        return len(self.interactions)

    @property
    def size(self) -> int:
        return len(self.interactions)

    def to_dict(self) -> dict[str, object]:
        return {
            "name": self.name,
            "skills": sorted(self.skills),
            "priority": self.priority,
            "open": self.is_open(),
            "size": self.size,
        }


@dataclass
class Recording:
    """Metadata about interaction recordings for compliance."""

    interaction_id: str
    started_at: datetime
    ended_at: Optional[datetime] = None
    redactions: List[str] = field(default_factory=list)
    retention_days: int = 30

    def close(self) -> None:
        self.ended_at = datetime.utcnow()

    def add_redaction(self, description: str) -> None:
        self.redactions.append(description)
