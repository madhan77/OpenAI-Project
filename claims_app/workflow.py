from __future__ import annotations

from typing import Iterable, Sequence

from .analytics import MetricsCollector
from .config import ClaimsAppConfig
from .models import (
    Claim,
    ClaimDecision,
    ClaimProcessingSummary,
    ClaimStatus,
    NotificationRecord,
    build_timeline_event,
)
from .notifications import NotificationContext, NotificationOrchestrator
from .payments import MockPaymentGateway, PaymentGateway, PaymentResult
from .repositories import ClaimRepository, InMemoryClaimRepository, ManualReviewItem, ManualReviewQueue
from .rules_engine import CompositeRuleEngine, FraudSignalRule, HighCostRule, OutOfNetworkRule, PriorAuthRule
from .validators import AttachmentValidator, CodingValidator, DuplicateClaimValidator, EligibilityValidator, ValidationIssue
from .repositories import ProcessedClaimTracker


class ClaimsProcessingApp:
    """Coordinates the formal claims processing workflow."""

    def __init__(
        self,
        *,
        config: ClaimsAppConfig | None = None,
        repository: ClaimRepository | None = None,
        metrics: MetricsCollector | None = None,
        notification_orchestrator: NotificationOrchestrator | None = None,
        payment_gateway: PaymentGateway | None = None,
        manual_queue: ManualReviewQueue | None = None,
        rule_engine: CompositeRuleEngine | None = None,
        validators: Iterable = (),
    ) -> None:
        self._config = config or ClaimsAppConfig()
        self._repository = repository or InMemoryClaimRepository()
        self._metrics = metrics or MetricsCollector()
        self._tracker = ProcessedClaimTracker()
        self._manual_queue = manual_queue or ManualReviewQueue()
        self._payment_gateway = payment_gateway or MockPaymentGateway()
        self._notification_orchestrator = notification_orchestrator
        if not self._notification_orchestrator:
            from .notifications import EmailChannel, PortalChannel, SMSChannel

            self._notification_orchestrator = NotificationOrchestrator(
                channels=[EmailChannel(), SMSChannel(), PortalChannel()]
            )
        self._rule_engine = rule_engine or CompositeRuleEngine(
            [
                HighCostRule(self._config),
                PriorAuthRule(),
                OutOfNetworkRule(),
                FraudSignalRule(),
            ]
        )
        self._validators: Sequence = tuple(
            validators
            or (
                EligibilityValidator(),
                AttachmentValidator(self._config),
                CodingValidator(),
                DuplicateClaimValidator(self._tracker, self._config),
            )
        )

    @property
    def metrics(self) -> MetricsCollector:
        return self._metrics

    @property
    def repository(self) -> ClaimRepository:
        return self._repository

    @property
    def manual_queue(self) -> ManualReviewQueue:
        return self._manual_queue

    def submit_claim(self, claim: Claim) -> None:
        """Persists an incoming claim and records intake metrics."""
        self._repository.save(claim)
        self._metrics.record("claims.intake", 1)

    def process_claim(self, claim_id: str) -> ClaimProcessingSummary:
        claim = self._repository.get(claim_id)
        if not claim:
            raise KeyError(f"Claim {claim_id} not found")

        events = list(self._repository.events(claim_id))
        events.append(build_timeline_event(ClaimStatus.VALIDATING, "Performing validation checks"))
        self._repository.record_event(claim_id, events[-1])
        self._repository.update_status(claim_id, ClaimStatus.VALIDATING)

        validation_issues: list[ValidationIssue] = []
        for validator in self._validators:
            validation_issues.extend(validator.validate(claim))

        if validation_issues:
            reason_codes = tuple(issue.code for issue in validation_issues)
            events.append(
                build_timeline_event(
                    ClaimStatus.PENDING_INFORMATION,
                    "Claim pending additional information",
                    missing=";".join(reason_codes),
                )
            )
            self._repository.record_event(claim_id, events[-1])
            self._repository.update_status(claim_id, ClaimStatus.PENDING_INFORMATION)
            self._metrics.record("claims.pending_info", 1, tags={"issues": ",".join(reason_codes)})
            self._tracker.record(claim)
            notification_records = self._notify(claim, ClaimDecision.PENDING_INFORMATION, reason_codes)
            return ClaimProcessingSummary(
                claim=claim,
                status=ClaimStatus.PENDING_INFORMATION,
                decision=ClaimDecision.PENDING_INFORMATION,
                reason_codes=reason_codes,
                events=tuple(events),
                notifications=notification_records,
            )

        rule_outcome = self._rule_engine.evaluate(claim)
        if rule_outcome.manual_review:
            reason_codes = tuple(rule_outcome.reason_codes)
            events.append(
                build_timeline_event(
                    ClaimStatus.MANUAL_REVIEW,
                    "Claim routed to manual review queue",
                    reasons=";".join(reason_codes),
                )
            )
            self._repository.record_event(claim_id, events[-1])
            self._repository.update_status(claim_id, ClaimStatus.MANUAL_REVIEW)
            priority = "urgent" if "POTENTIAL_FRAUD" in reason_codes else "standard"
            self._manual_queue.enqueue(ManualReviewItem(claim_id=claim_id, reason_codes=list(reason_codes), priority=priority))
            self._metrics.record("claims.manual_review", 1, tags={"reasons": ",".join(reason_codes)})
            self._tracker.record(claim)
            notification_records = self._notify(claim, ClaimDecision.NEEDS_MANUAL_REVIEW, reason_codes)
            return ClaimProcessingSummary(
                claim=claim,
                status=ClaimStatus.MANUAL_REVIEW,
                decision=ClaimDecision.NEEDS_MANUAL_REVIEW,
                reason_codes=reason_codes,
                events=tuple(events),
                notifications=notification_records,
            )

        self._repository.update_status(claim_id, ClaimStatus.AUTO_ADJUDICATED)
        events.append(build_timeline_event(ClaimStatus.AUTO_ADJUDICATED, "Claim auto-adjudicated"))
        self._repository.record_event(claim_id, events[-1])

        payment_result: PaymentResult = self._payment_gateway.issue_payment(claim, self._config)
        events.append(build_timeline_event(ClaimStatus.DECIDED, "Claim approved"))
        self._repository.record_event(claim_id, events[-1])
        self._repository.update_status(claim_id, ClaimStatus.PAYMENT_INSTRUCTED)
        events.append(
            build_timeline_event(
                ClaimStatus.PAYMENT_INSTRUCTED,
                "Payment instruction generated",
                payment_reference=payment_result.instruction.reference_id,
            )
        )
        self._repository.record_event(claim_id, events[-1])
        self._metrics.record("claims.auto_adjudicated", 1)
        self._tracker.record(claim)

        notification_records = self._notify(claim, ClaimDecision.APPROVED, rule_outcome.reason_codes)
        self._repository.update_status(claim_id, ClaimStatus.NOTIFIED)
        events.append(build_timeline_event(ClaimStatus.NOTIFIED, "Stakeholders notified"))
        self._repository.record_event(claim_id, events[-1])

        return ClaimProcessingSummary(
            claim=claim,
            status=ClaimStatus.NOTIFIED,
            decision=ClaimDecision.APPROVED,
            reason_codes=rule_outcome.reason_codes,
            events=tuple(events),
            notifications=notification_records,
            payment_instruction=payment_result.instruction,
            eob=payment_result.eob,
        )

    def _notify(
        self,
        claim: Claim,
        decision: ClaimDecision,
        reason_codes: Sequence[str],
    ) -> Sequence[NotificationRecord]:
        context = NotificationContext(
            claim=claim,
            decision=decision,
            reason_codes=reason_codes,
            recipients={
                "provider_email": claim.metadata.get("provider_email", "provider@example.com"),
                "provider_sms": claim.metadata.get("provider_sms", "+10000000000"),
                "portal_user": claim.member_id,
            },
        )
        records = self._notification_orchestrator.dispatch(context)
        for record in records:
            self._metrics.record("claims.notifications", 1, tags={"channel": record.channel})
        return records


__all__ = ["ClaimsProcessingApp"]
