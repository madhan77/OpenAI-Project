"""In-memory telephony adapter backed by mock data."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, Optional


class TelephonyIntegrationError(RuntimeError):
    """Raised when the mock telephony provider cannot fulfil a request."""


@dataclass
class CallSession:
    """Represents the lifecycle of a call bridged through the mock provider."""

    call_sid: str
    interaction_id: str
    queue: str
    agent_id: Optional[str] = None
    customer_number: Optional[str] = None
    recording_sid: Optional[str] = None
    metadata: Dict[str, str] = field(default_factory=dict)


class MockTelephonyGateway:
    """Simple in-memory telephony implementation used for demos and tests."""

    def __init__(self) -> None:
        self._sessions: Dict[str, CallSession] = {}
        self._recordings: Dict[str, bytes] = {
            "rec-001": b"MOCK RECORDING DATA",
            "rec-002": b"ADDITIONAL SAMPLE",
        }

    async def initiate_call(self, from_number: str, to_number: str, *, interaction_id: str) -> CallSession:
        call_sid = f"CA{len(self._sessions) + 1:08d}"
        session = CallSession(
            call_sid=call_sid,
            interaction_id=interaction_id,
            queue="outbound",
            customer_number=to_number,
        )
        self._sessions[call_sid] = session
        return session

    async def bridge_agent(self, call_sid: str, agent_number: str) -> None:
        session = self._sessions.get(call_sid)
        if session is None:
            raise TelephonyIntegrationError("Unknown call session")
        session.agent_id = agent_number

    async def fetch_recording(self, recording_sid: str) -> bytes:
        if recording_sid not in self._recordings:
            raise TelephonyIntegrationError("Recording not found")
        return self._recordings[recording_sid]

    async def update_call_metadata(self, call_sid: str, *, metadata: Dict[str, str]) -> None:
        session = self._sessions.get(call_sid)
        if session is None:
            raise TelephonyIntegrationError("Unknown call session")
        session.metadata.update(metadata)

    async def close(self) -> None:  # pragma: no cover - retained for API parity
        self._sessions.clear()


__all__ = ["MockTelephonyGateway", "TelephonyIntegrationError", "CallSession"]
