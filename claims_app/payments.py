from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import List, Protocol, Sequence

from .config import ClaimsAppConfig
from .models import Claim, ClaimLine, ExplanationOfBenefits, FinancialBreakdown, PaymentInstruction, now


@dataclass(slots=True)
class PaymentResult:
    instruction: PaymentInstruction
    eob: ExplanationOfBenefits


class PaymentGateway(Protocol):
    def issue_payment(self, claim: Claim, config: ClaimsAppConfig) -> PaymentResult:
        ...


class MockPaymentGateway:
    """Generates an explanation of benefits and payment instruction."""

    def issue_payment(self, claim: Claim, config: ClaimsAppConfig) -> PaymentResult:
        allowed_lines: List[FinancialBreakdown] = []
        total_allowed = 0.0
        total_paid = 0.0
        for line in claim.service_lines:
            allowed = line.allowed_amount if line.allowed_amount is not None else line.charge_amount * 0.85
            member_resp = allowed * 0.2
            payer_resp = allowed - member_resp
            total_allowed += allowed
            total_paid += payer_resp
            allowed_lines.append(
                FinancialBreakdown(
                    allowed_amount=allowed,
                    payer_responsibility=payer_resp,
                    member_responsibility=member_resp,
                    notes=line.notes,
                )
            )
        eob_id = f"EOB-{claim.claim_id}"
        eob = ExplanationOfBenefits(
            claim_id=claim.claim_id,
            eob_id=eob_id,
            issued_at=now(),
            lines=tuple(allowed_lines),
            total_allowed=total_allowed,
            total_paid=total_paid,
            total_member_responsibility=total_allowed - total_paid,
        )
        instruction = PaymentInstruction(
            claim_id=claim.claim_id,
            total_payment=total_paid,
            method=config.payment_method,
            scheduled_for=now() + config.payment_cadence,
            reference_id=f"PAY-{claim.claim_id}",
        )
        return PaymentResult(instruction=instruction, eob=eob)


__all__ = ["MockPaymentGateway", "PaymentGateway", "PaymentResult"]
