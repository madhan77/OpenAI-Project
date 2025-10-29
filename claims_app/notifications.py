from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Dict, Iterable, List, Protocol, Sequence

from .models import Claim, ClaimDecision, NotificationRecord, now


@dataclass(slots=True)
class NotificationContext:
    claim: Claim
    decision: ClaimDecision
    reason_codes: Sequence[str]
    recipients: Dict[str, str]


class NotificationChannel(Protocol):
    name: str

    def send(self, context: NotificationContext) -> NotificationRecord:
        ...


class EmailChannel:
    name = "email"

    def send(self, context: NotificationContext) -> NotificationRecord:
        recipient = context.recipients.get("provider_email", "provider@example.com")
        message = f"Claim {context.claim.claim_id} decision: {context.decision.name}"
        return NotificationRecord(channel=self.name, recipient=recipient, message=message, sent_at=now())


class SMSChannel:
    name = "sms"

    def send(self, context: NotificationContext) -> NotificationRecord:
        recipient = context.recipients.get("provider_sms", "+10000000000")
        message = f"Claim {context.claim.claim_id} status {context.decision.name}"
        return NotificationRecord(channel=self.name, recipient=recipient, message=message, sent_at=now())


class PortalChannel:
    name = "portal"

    def send(self, context: NotificationContext) -> NotificationRecord:
        recipient = context.recipients.get("portal_user", context.claim.member_id)
        message = "Portal updated with new claim status"
        return NotificationRecord(channel=self.name, recipient=recipient, message=message, sent_at=now())


class NotificationOrchestrator:
    """Dispatches notifications to configured channels."""

    def __init__(self, channels: Iterable[NotificationChannel]):
        self._channels = tuple(channels)

    def dispatch(self, context: NotificationContext) -> Sequence[NotificationRecord]:
        records: List[NotificationRecord] = []
        for channel in self._channels:
            records.append(channel.send(context))
        return tuple(records)


__all__ = [
    "EmailChannel",
    "NotificationChannel",
    "NotificationContext",
    "NotificationOrchestrator",
    "PortalChannel",
    "SMSChannel",
]
