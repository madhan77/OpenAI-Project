from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, List, Protocol, Sequence

from .config import ClaimsAppConfig
from .models import Claim


@dataclass(slots=True)
class RuleOutcome:
    passed: bool
    reason_codes: Sequence[str] = ()
    manual_review: bool = False


class Rule(Protocol):
    def evaluate(self, claim: Claim) -> RuleOutcome:
        ...


class HighCostRule:
    """Routes high dollar claims to manual review."""

    def __init__(self, config: ClaimsAppConfig) -> None:
        self._config = config

    def evaluate(self, claim: Claim) -> RuleOutcome:
        total = claim.total_charge()
        if total >= self._config.high_cost_manual_threshold:
            return RuleOutcome(False, ("HIGH_DOLLAR",), manual_review=True)
        if total > self._config.auto_approval_threshold:
            return RuleOutcome(True, ("REQUIRES_SUPERVISOR_REVIEW",))
        return RuleOutcome(True)


class PriorAuthRule:
    """Checks for prior authorization attachments when flagged."""

    def evaluate(self, claim: Claim) -> RuleOutcome:
        if claim.metadata.get("requires_prior_auth") and "PRIOR_AUTH" not in claim.attachments:
            return RuleOutcome(False, ("MISSING_PRIOR_AUTH",), manual_review=True)
        return RuleOutcome(True)


class OutOfNetworkRule:
    """Flags out-of-network providers for manual review."""

    def evaluate(self, claim: Claim) -> RuleOutcome:
        if claim.provider and not claim.provider.in_network:
            return RuleOutcome(False, ("OUT_OF_NETWORK",), manual_review=True)
        return RuleOutcome(True)


class FraudSignalRule:
    """Flags claims with potential fraud indicators in metadata."""

    def evaluate(self, claim: Claim) -> RuleOutcome:
        if claim.metadata.get("fraud_score") == "high":
            return RuleOutcome(False, ("POTENTIAL_FRAUD",), manual_review=True)
        return RuleOutcome(True)


class CompositeRuleEngine:
    """Evaluates a sequence of rules and aggregates outcomes."""

    def __init__(self, rules: Iterable[Rule]):
        self._rules = tuple(rules)

    def evaluate(self, claim: Claim) -> RuleOutcome:
        reason_codes: List[str] = []
        manual_review = False
        for rule in self._rules:
            outcome = rule.evaluate(claim)
            if not outcome.passed:
                reason_codes.extend(outcome.reason_codes)
            manual_review = manual_review or outcome.manual_review
        passed = not manual_review and not reason_codes
        return RuleOutcome(passed=passed, reason_codes=tuple(reason_codes), manual_review=manual_review)


__all__ = [
    "CompositeRuleEngine",
    "FraudSignalRule",
    "HighCostRule",
    "OutOfNetworkRule",
    "PriorAuthRule",
    "Rule",
    "RuleOutcome",
]
