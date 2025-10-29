from dataclasses import replace
from datetime import datetime
from pathlib import Path
import sys

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from agents import (
    Claim,
    ClaimDecision,
    ClaimLine,
    ClaimStatus,
    ClaimsProcessingAgent,
    ClaimsProcessingAgentConfig,
    HeuristicRulesEngine,
    InMemoryAnalyticsSink,
)


@pytest.fixture
def base_claim() -> Claim:
    return Claim(
        claim_id="CLM123",
        member_id="MBR123",
        provider_id="PRV456",
        submitted_at=datetime(2024, 1, 1, 12, 0, 0),
        service_lines=[
            ClaimLine(code="99213", description="Office visit", charge_amount=100.0),
        ],
        attachments={"REFERRAL": "ref123", "PRIOR_AUTH": "auth456"},
    )


def test_auto_adjudication_success(base_claim: Claim) -> None:
    sink = InMemoryAnalyticsSink()
    agent = ClaimsProcessingAgent(analytics_sink=sink)

    result = agent.process(base_claim)

    assert result.status is ClaimStatus.NOTIFIED
    assert result.decision is ClaimDecision.APPROVED
    assert any(event.status is ClaimStatus.AUTO_ADJUDICATED for event in result.events)
    metrics = {record["metric"]: record for record in sink.records}
    assert "claims.auto_approved" in metrics


def test_routes_to_manual_review_when_threshold_exceeded(base_claim: Claim) -> None:
    expensive_claim = replace(
        base_claim,
        service_lines=[
            ClaimLine(code="27447", description="Knee replacement", charge_amount=3500.0),
        ],
    )
    config = ClaimsProcessingAgentConfig(auto_approval_threshold=500.0)
    engine = HeuristicRulesEngine(config)
    agent = ClaimsProcessingAgent(config=config, rules_engine=engine)

    result = agent.process(expensive_claim)

    assert result.status is ClaimStatus.ROUTED_TO_ANALYST
    assert result.decision is None
    assert "HIGH_DOLLAR" in result.reason_codes


def test_pending_information_when_missing_attachments(base_claim: Claim) -> None:
    claim = Claim(
        claim_id=base_claim.claim_id,
        member_id=base_claim.member_id,
        provider_id=base_claim.provider_id,
        submitted_at=base_claim.submitted_at,
        service_lines=base_claim.service_lines,
        attachments={},
    )

    agent = ClaimsProcessingAgent()

    result = agent.process(claim)

    assert result.status is ClaimStatus.PENDING_INFO
    assert result.decision is ClaimDecision.PENDING_INFORMATION
    assert "MISSING_REFERRAL" in result.reason_codes
    assert "MISSING_PRIOR_AUTH" in result.reason_codes


@pytest.mark.parametrize(
    "amount, expected", [(10.0, []), (0.0, ["INVALID_CHARGE_AMOUNT"]), (-1.0, ["INVALID_CHARGE_AMOUNT"])]
)
def test_validation_of_charge_amounts(base_claim: Claim, amount: float, expected: list[str]) -> None:
    claim = Claim(
        claim_id=base_claim.claim_id,
        member_id=base_claim.member_id,
        provider_id=base_claim.provider_id,
        submitted_at=base_claim.submitted_at,
        service_lines=[ClaimLine(code="99213", description="Office visit", charge_amount=amount)],
        attachments=base_claim.attachments,
    )

    agent = ClaimsProcessingAgent()

    errors = agent._validate_claim(claim)

    for code in expected:
        assert code in errors
    if not expected:
        assert "INVALID_CHARGE_AMOUNT" not in errors
