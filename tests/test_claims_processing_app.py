from datetime import datetime, timedelta, date
from pathlib import Path
import sys

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from claims_app import (
    Claim,
    ClaimLine,
    ClaimsAppConfig,
    ClaimsProcessingApp,
    ClaimStatus,
    MemberProfile,
    ProviderProfile,
)


@pytest.fixture
def member_profile() -> MemberProfile:
    return MemberProfile(
        member_id="MBR123",
        coverage_start=date(2023, 1, 1),
        coverage_end=date(2025, 1, 1),
        plan_id="PLAN-A",
    )


@pytest.fixture
def provider_profile() -> ProviderProfile:
    return ProviderProfile(
        provider_id="PRV456",
        npi="1234567890",
        in_network=True,
        specialties=("SURGERY",),
    )


@pytest.fixture
def base_claim(member_profile: MemberProfile, provider_profile: ProviderProfile) -> Claim:
    return Claim(
        claim_id="CLM123",
        member_id=member_profile.member_id,
        provider_id=provider_profile.provider_id,
        submitted_at=datetime(2024, 5, 1, 10, 0, 0),
        service_lines=[
            ClaimLine(code="27447", description="Total knee arthroplasty", charge_amount=4000.0, units=1),
            ClaimLine(code="J1100", description="Injection", charge_amount=150.0, units=2),
        ],
        attachments={"PRIOR_AUTH": "AUTH123", "OPERATIVE_REPORT": "DOC456"},
        metadata={"service_categories": "SURGERY", "provider_email": "ortho@example.com"},
        member=member_profile,
        provider=provider_profile,
    )


def test_auto_adjudication_generates_payment_and_notifications(base_claim: Claim) -> None:
    config = ClaimsAppConfig(auto_approval_threshold=5000.0, high_cost_manual_threshold=7500.0)
    app = ClaimsProcessingApp(config=config)

    app.submit_claim(base_claim)
    summary = app.process_claim(base_claim.claim_id)

    assert summary.status is ClaimStatus.NOTIFIED
    assert summary.decision.name == "APPROVED"
    assert summary.payment_instruction is not None
    assert summary.eob is not None
    assert summary.payment_instruction.total_payment > 0
    assert {record.channel for record in summary.notifications} == {"email", "sms", "portal"}
    assert app.metrics.counter("claims.auto_adjudicated") == 1


def test_manual_review_routes_to_queue_when_high_cost(base_claim: Claim) -> None:
    config = ClaimsAppConfig(auto_approval_threshold=500.0, high_cost_manual_threshold=2000.0)
    app = ClaimsProcessingApp(config=config)

    app.submit_claim(base_claim)
    summary = app.process_claim(base_claim.claim_id)

    assert summary.status is ClaimStatus.MANUAL_REVIEW
    queue_items = app.manual_queue.list_items()
    assert queue_items and queue_items[0].claim_id == base_claim.claim_id
    assert "HIGH_DOLLAR" in summary.reason_codes


def test_pending_information_when_missing_documents(
    base_claim: Claim, member_profile: MemberProfile, provider_profile: ProviderProfile
) -> None:
    claim = Claim(
        claim_id="CLM124",
        member_id=member_profile.member_id,
        provider_id=provider_profile.provider_id,
        submitted_at=base_claim.submitted_at,
        service_lines=base_claim.service_lines,
        attachments={},
        metadata={"service_categories": "SURGERY"},
        member=member_profile,
        provider=provider_profile,
    )
    app = ClaimsProcessingApp()

    app.submit_claim(claim)
    summary = app.process_claim(claim.claim_id)

    assert summary.status is ClaimStatus.PENDING_INFORMATION
    assert "MISSING_SURGERY" in summary.reason_codes


def test_duplicate_claim_validation_flags_recent_submissions(base_claim: Claim) -> None:
    app = ClaimsProcessingApp()

    app.submit_claim(base_claim)
    app.process_claim(base_claim.claim_id)

    duplicate_claim = Claim(
        claim_id=base_claim.claim_id,
        member_id=base_claim.member_id,
        provider_id=base_claim.provider_id,
        submitted_at=base_claim.submitted_at + timedelta(days=1),
        service_lines=base_claim.service_lines,
        attachments=base_claim.attachments,
        metadata=base_claim.metadata,
        member=base_claim.member,
        provider=base_claim.provider,
    )

    app.submit_claim(duplicate_claim)
    summary = app.process_claim(duplicate_claim.claim_id)

    assert summary.status is ClaimStatus.PENDING_INFORMATION
    assert "POTENTIAL_DUPLICATE" in summary.reason_codes
