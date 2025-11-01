from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, date
from enum import Enum, auto
from typing import Dict, Iterable, List, Optional, Sequence


class ClaimStatus(Enum):
    """Lifecycle states for a claim inside the platform."""

    RECEIVED = auto()
    VALIDATING = auto()
    PENDING_INFORMATION = auto()
    READY_FOR_REVIEW = auto()
    AUTO_ADJUDICATED = auto()
    MANUAL_REVIEW = auto()
    DECIDED = auto()
    PAYMENT_INSTRUCTED = auto()
    NOTIFIED = auto()


class ClaimDecision(Enum):
    """Decision outcomes supported by the app."""

    APPROVED = auto()
    DENIED = auto()
    PARTIAL_APPROVAL = auto()
    PENDING_INFORMATION = auto()
    NEEDS_MANUAL_REVIEW = auto()


@dataclass(slots=True)
class ClaimLine:
    code: str
    description: str
    charge_amount: float
    units: int = 1
    allowed_amount: Optional[float] = None
    notes: List[str] = field(default_factory=list)


@dataclass(slots=True)
class MemberProfile:
    member_id: str
    coverage_start: date
    coverage_end: Optional[date]
    plan_id: str
    flags: Dict[str, str] = field(default_factory=dict)

    def is_active_on(self, day: date) -> bool:
        if day < self.coverage_start:
            return False
        if self.coverage_end and day > self.coverage_end:
            return False
        return True


@dataclass(slots=True)
class ProviderProfile:
    provider_id: str
    npi: str
    in_network: bool
    specialties: Sequence[str] = ()
    flags: Dict[str, str] = field(default_factory=dict)


@dataclass(slots=True)
class Claim:
    claim_id: str
    member_id: str
    provider_id: str
    submitted_at: datetime
    service_lines: List[ClaimLine]
    attachments: Dict[str, str] = field(default_factory=dict)
    metadata: Dict[str, str] = field(default_factory=dict)
    member: Optional[MemberProfile] = None
    provider: Optional[ProviderProfile] = None

    def total_charge(self) -> float:
        return sum(line.charge_amount * line.units for line in self.service_lines)


@dataclass(slots=True)
class ClaimEvent:
    timestamp: datetime
    status: ClaimStatus
    message: str
    data: Dict[str, str] = field(default_factory=dict)


@dataclass(slots=True)
class FinancialBreakdown:
    allowed_amount: float
    payer_responsibility: float
    member_responsibility: float
    notes: Sequence[str] = ()


@dataclass(slots=True)
class PaymentInstruction:
    claim_id: str
    total_payment: float
    method: str
    scheduled_for: datetime
    reference_id: str


@dataclass(slots=True)
class ExplanationOfBenefits:
    claim_id: str
    eob_id: str
    issued_at: datetime
    lines: Sequence[FinancialBreakdown]
    total_allowed: float
    total_paid: float
    total_member_responsibility: float


@dataclass(slots=True)
class NotificationRecord:
    channel: str
    recipient: str
    message: str
    sent_at: datetime


@dataclass(slots=True)
class ClaimProcessingSummary:
    claim: Claim
    status: ClaimStatus
    decision: ClaimDecision
    reason_codes: Sequence[str]
    events: Sequence[ClaimEvent]
    notifications: Sequence[NotificationRecord]
    payment_instruction: Optional[PaymentInstruction] = None
    eob: Optional[ExplanationOfBenefits] = None


def now() -> datetime:
    return datetime.utcnow()


def build_timeline_event(status: ClaimStatus, message: str, **data: str) -> ClaimEvent:
    return ClaimEvent(timestamp=now(), status=status, message=message, data=dict(data))


__all__ = [
    "Claim",
    "ClaimDecision",
    "ClaimEvent",
    "ClaimLine",
    "ClaimProcessingSummary",
    "ClaimStatus",
    "ExplanationOfBenefits",
    "FinancialBreakdown",
    "MemberProfile",
    "NotificationRecord",
    "PaymentInstruction",
    "ProviderProfile",
    "build_timeline_event",
    "now",
]
