"""Core logic for the ClaimsProcessing agent.

The implementation translates the product requirements document (PRD) and agent design
into executable behaviour. The goal is not to replace a production-grade adjudication
system, but to provide a high-fidelity reference implementation that demonstrates how
a digital co-pilot can orchestrate the end-to-end workflow.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum, auto
from typing import Dict, List, Optional, Protocol, Sequence


class ClaimStatus(Enum):
    """High-level lifecycle states for a claim."""

    RECEIVED = auto()
    VALIDATING = auto()
    PENDING_INFO = auto()
    AUTO_ADJUDICATED = auto()
    ROUTED_TO_ANALYST = auto()
    DECIDED = auto()
    NOTIFIED = auto()


class ClaimDecision(Enum):
    """Final decision outcomes supported by the agent."""

    APPROVED = auto()
    DENIED = auto()
    PARTIAL_APPROVAL = auto()
    PENDING_INFORMATION = auto()


@dataclass(slots=True)
class ClaimLine:
    """Represents a single service line on the claim."""

    code: str
    description: str
    charge_amount: float
    allowed_amount: Optional[float] = None
    notes: List[str] = field(default_factory=list)


@dataclass(slots=True)
class Claim:
    """Normalized claim payload consumed by the agent."""

    claim_id: str
    member_id: str
    provider_id: str
    submitted_at: datetime
    service_lines: List[ClaimLine]
    attachments: Dict[str, str] = field(default_factory=dict)
    metadata: Dict[str, str] = field(default_factory=dict)

    def total_charge(self) -> float:
        return sum(line.charge_amount for line in self.service_lines)


@dataclass(slots=True)
class ClaimEvent:
    """Timeline event produced during processing."""

    timestamp: datetime
    status: ClaimStatus
    message: str
    data: Dict[str, str] = field(default_factory=dict)


@dataclass(slots=True)
class ClaimProcessingResult:
    """Final outcome of an adjudicated claim."""

    claim: Claim
    status: ClaimStatus
    decision: Optional[ClaimDecision]
    reason_codes: Sequence[str]
    events: Sequence[ClaimEvent]


class ClaimProcessingError(RuntimeError):
    """Raised when the agent cannot safely progress a claim."""


class RuleEvaluation(Protocol):
    """Protocol for rule engine evaluations."""

    @property
    def passed(self) -> bool:  # pragma: no cover - protocol
        ...

    @property
    def reason_codes(self) -> Sequence[str]:  # pragma: no cover - protocol
        ...

    @property
    def requires_manual_review(self) -> bool:  # pragma: no cover - protocol
        ...


class RulesEngine(Protocol):
    """Contract implemented by policy/rules engines."""

    def evaluate(self, claim: Claim) -> RuleEvaluation:  # pragma: no cover - protocol
        ...


class NotificationGateway(Protocol):
    """Contract for delivering notifications to stakeholders."""

    def notify(self, claim: Claim, decision: Optional[ClaimDecision], message: str) -> None:
        ...


class AnalyticsSink(Protocol):
    """Contract for operational analytics."""

    def record(self, metric: str, value: float, tags: Optional[Dict[str, str]] = None) -> None:
        ...


@dataclass(slots=True)
class ClaimsProcessingAgentConfig:
    """Configuration knobs to adapt the agent to payer policy."""

    auto_approval_threshold: float = 500.0
    missing_attachment_codes: Sequence[str] = ("REFERRAL", "PRIOR_AUTH")
    manual_review_tags: Dict[str, str] = field(default_factory=dict)


class DefaultRuleEvaluation:
    """Simple implementation of :class:`RuleEvaluation`."""

    def __init__(self, passed: bool, reason_codes: Sequence[str], requires_manual_review: bool) -> None:
        self._passed = passed
        self._reason_codes = tuple(reason_codes)
        self._requires_manual_review = requires_manual_review

    @property
    def passed(self) -> bool:
        return self._passed

    @property
    def reason_codes(self) -> Sequence[str]:
        return self._reason_codes

    @property
    def requires_manual_review(self) -> bool:
        return self._requires_manual_review


class HeuristicRulesEngine:
    """A pragmatic rule engine suitable for demonstrations and tests."""

    def __init__(self, config: ClaimsProcessingAgentConfig) -> None:
        self._config = config

    def evaluate(self, claim: Claim) -> RuleEvaluation:
        reason_codes: List[str] = []
        requires_manual_review = False

        if claim.total_charge() > self._config.auto_approval_threshold:
            reason_codes.append("HIGH_DOLLAR")
            requires_manual_review = True

        missing_docs = [code for code in self._config.missing_attachment_codes if code not in claim.attachments]
        if missing_docs:
            reason_codes.extend(f"MISSING_{code}" for code in missing_docs)
            requires_manual_review = True

        if claim.metadata.get("prior_denials"):
            reason_codes.append("HAS_PRIOR_DENIALS")
            requires_manual_review = True

        passed = not requires_manual_review
        return DefaultRuleEvaluation(passed=passed, reason_codes=reason_codes, requires_manual_review=requires_manual_review)


class ConsoleNotificationGateway:
    """Notification gateway that writes to stdout."""

    def notify(self, claim: Claim, decision: Optional[ClaimDecision], message: str) -> None:
        print(f"[NOTIFY] claim={claim.claim_id} decision={decision} message={message}")


class InMemoryAnalyticsSink:
    """Captures metrics in-memory for inspection during tests."""

    def __init__(self) -> None:
        self.records: List[Dict[str, object]] = []

    def record(self, metric: str, value: float, tags: Optional[Dict[str, str]] = None) -> None:
        self.records.append({"metric": metric, "value": value, "tags": dict(tags or {})})


class ClaimsProcessingAgent:
    """End-to-end orchestration of the claims processing workflow."""

    def __init__(
        self,
        *,
        config: Optional[ClaimsProcessingAgentConfig] = None,
        rules_engine: Optional[RulesEngine] = None,
        notification_gateway: Optional[NotificationGateway] = None,
        analytics_sink: Optional[AnalyticsSink] = None,
    ) -> None:
        self._config = config or ClaimsProcessingAgentConfig()
        self._rules_engine = rules_engine or HeuristicRulesEngine(self._config)
        self._notification_gateway = notification_gateway or ConsoleNotificationGateway()
        self._analytics_sink = analytics_sink or InMemoryAnalyticsSink()

    def process(self, claim: Claim) -> ClaimProcessingResult:
        """Process a claim from intake through decision and notification."""

        timeline: List[ClaimEvent] = []

        def record(status: ClaimStatus, message: str, **data: str) -> None:
            timeline.append(ClaimEvent(timestamp=datetime.utcnow(), status=status, message=message, data=data))

        record(ClaimStatus.RECEIVED, "Claim received and queued for validation.")
        record(ClaimStatus.VALIDATING, "Running automated validation checks.")

        validation_errors = self._validate_claim(claim)
        if validation_errors:
            record(
                ClaimStatus.PENDING_INFO,
                "Claim requires additional information before proceeding.",
                missing=",".join(validation_errors),
            )
            decision = ClaimDecision.PENDING_INFORMATION
            self._notify(claim, decision, "Additional documentation required.")
            self._record_metric("claims.pending_information", 1, {"count": str(len(validation_errors))})
            return ClaimProcessingResult(
                claim=claim,
                status=ClaimStatus.PENDING_INFO,
                decision=decision,
                reason_codes=validation_errors,
                events=tuple(timeline),
            )

        evaluation = self._rules_engine.evaluate(claim)
        if evaluation.requires_manual_review:
            record(
                ClaimStatus.ROUTED_TO_ANALYST,
                "Claim routed for manual review due to rule triggers.",
                reason_codes=",".join(evaluation.reason_codes),
            )
            self._record_metric("claims.manual_review", 1, {"reason": ";".join(evaluation.reason_codes)})
            self._notify(claim, None, "Claim routed to analyst for further review.")
            return ClaimProcessingResult(
                claim=claim,
                status=ClaimStatus.ROUTED_TO_ANALYST,
                decision=None,
                reason_codes=evaluation.reason_codes,
                events=tuple(timeline),
            )

        record(ClaimStatus.AUTO_ADJUDICATED, "Claim auto-adjudicated successfully.")
        decision = ClaimDecision.APPROVED
        record(ClaimStatus.DECIDED, "Claim approved and payment instructions generated.")
        self._record_metric("claims.auto_approved", 1)
        self._notify(claim, decision, "Claim approved via auto-adjudication.")
        record(ClaimStatus.NOTIFIED, "Stakeholders notified of adjudication outcome.")

        return ClaimProcessingResult(
            claim=claim,
            status=ClaimStatus.NOTIFIED,
            decision=decision,
            reason_codes=evaluation.reason_codes,
            events=tuple(timeline),
        )

    def _validate_claim(self, claim: Claim) -> List[str]:
        errors: List[str] = []
        if not claim.service_lines:
            errors.append("NO_SERVICE_LINES")
        for code in self._config.missing_attachment_codes:
            if code not in claim.attachments:
                errors.append(f"MISSING_{code}")
        if any(line.charge_amount <= 0 for line in claim.service_lines):
            errors.append("INVALID_CHARGE_AMOUNT")
        return errors

    def _notify(self, claim: Claim, decision: Optional[ClaimDecision], message: str) -> None:
        self._notification_gateway.notify(claim, decision, message)

    def _record_metric(self, metric: str, value: float, tags: Optional[Dict[str, str]] = None) -> None:
        self._analytics_sink.record(metric, value, tags)

    @property
    def analytics_sink(self) -> AnalyticsSink:
        return self._analytics_sink


def build_default_agent() -> ClaimsProcessingAgent:
    """Helper for callers who simply need the default configuration."""

    return ClaimsProcessingAgent()


__all__ = [
    "AnalyticsSink",
    "Claim",
    "ClaimDecision",
    "ClaimEvent",
    "ClaimLine",
    "ClaimProcessingError",
    "ClaimProcessingResult",
    "ClaimStatus",
    "ClaimsProcessingAgent",
    "ClaimsProcessingAgentConfig",
    "ConsoleNotificationGateway",
    "DefaultRuleEvaluation",
    "HeuristicRulesEngine",
    "InMemoryAnalyticsSink",
    "NotificationGateway",
    "RuleEvaluation",
    "RulesEngine",
    "build_default_agent",
]
