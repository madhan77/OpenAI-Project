from __future__ import annotations

from dataclasses import dataclass
from datetime import timedelta
from typing import Iterable, List, Protocol, Sequence

from .config import ClaimsAppConfig
from .models import Claim, MemberProfile, ProviderProfile
from .repositories import ProcessedClaimTracker


@dataclass(slots=True)
class ValidationIssue:
    code: str
    message: str


class Validator(Protocol):
    def validate(self, claim: Claim) -> Sequence[ValidationIssue]:
        ...


class EligibilityValidator:
    """Validates member coverage and provider network status."""

    def validate(self, claim: Claim) -> Sequence[ValidationIssue]:
        issues: List[ValidationIssue] = []
        member: MemberProfile | None = claim.member
        provider: ProviderProfile | None = claim.provider

        if not member:
            issues.append(ValidationIssue("MISSING_MEMBER_PROFILE", "Member profile missing"))
        else:
            if not member.is_active_on(claim.submitted_at.date()):
                issues.append(ValidationIssue("MEMBER_NOT_ACTIVE", "Member coverage inactive on service date"))
        if not provider:
            issues.append(ValidationIssue("MISSING_PROVIDER_PROFILE", "Provider profile missing"))
        elif not provider.in_network:
            issues.append(ValidationIssue("OUT_OF_NETWORK", "Provider is out of network"))
        return issues


class AttachmentValidator:
    """Ensures required documentation is supplied based on metadata tags."""

    def __init__(self, config: ClaimsAppConfig) -> None:
        self._config = config

    def validate(self, claim: Claim) -> Sequence[ValidationIssue]:
        issues: List[ValidationIssue] = []
        for qualifier, required in self._config.required_attachments.items():
            if qualifier in claim.metadata.get("service_categories", "").split(","):
                missing = [code for code in required if code not in claim.attachments]
                if missing:
                    issues.append(
                        ValidationIssue(
                            code=f"MISSING_{qualifier}",
                            message=f"Missing required attachments: {', '.join(missing)}",
                        )
                    )
        return issues


class DuplicateClaimValidator:
    """Detects recently submitted duplicates using the tracker."""

    def __init__(self, tracker: ProcessedClaimTracker, config: ClaimsAppConfig) -> None:
        self._tracker = tracker
        self._config = config

    def validate(self, claim: Claim) -> Sequence[ValidationIssue]:
        if self._tracker.seen_recently(claim, timedelta(days=self._config.duplicate_window_days)):
            return [ValidationIssue("POTENTIAL_DUPLICATE", "Claim was submitted in the duplicate window")]
        return []


class CodingValidator:
    """Basic code validation and edits to mimic clinical scrubbing."""

    NON_BILLABLE_CODES = {"00000", "99999"}

    def validate(self, claim: Claim) -> Sequence[ValidationIssue]:
        issues: List[ValidationIssue] = []
        if not claim.service_lines:
            issues.append(ValidationIssue("NO_SERVICE_LINES", "Claim missing service lines"))
        for line in claim.service_lines:
            if line.code in self.NON_BILLABLE_CODES:
                issues.append(ValidationIssue("NON_BILLABLE_CODE", f"Code {line.code} is not billable"))
            if line.charge_amount <= 0:
                issues.append(ValidationIssue("INVALID_CHARGE", f"Line {line.code} has invalid charge amount"))
        return issues


__all__ = [
    "AttachmentValidator",
    "CodingValidator",
    "DuplicateClaimValidator",
    "EligibilityValidator",
    "ValidationIssue",
    "Validator",
]
