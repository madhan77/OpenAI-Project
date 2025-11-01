from __future__ import annotations

from dataclasses import dataclass, field
from datetime import timedelta
from typing import Dict, Iterable, Mapping, Sequence


@dataclass(slots=True)
class ClaimsAppConfig:
    """Configuration model for the claims processing platform."""

    auto_approval_threshold: float = 750.0
    high_cost_manual_threshold: float = 5000.0
    required_attachments: Mapping[str, Sequence[str]] = field(
        default_factory=lambda: {
            "SURGERY": ("PRIOR_AUTH", "OPERATIVE_REPORT"),
            "SPECIALIST": ("REFERRAL",),
        }
    )
    duplicate_window_days: int = 30
    manual_review_tags: Mapping[str, str] = field(
        default_factory=lambda: {
            "HIGH_DOLLAR": "High dollar claim requiring senior analyst",
            "OUT_OF_NETWORK": "Provider flagged as out of network",
            "POTENTIAL_FRAUD": "Fraud signal triggered",
        }
    )
    payment_method: str = "ACH"
    payment_cadence: timedelta = timedelta(days=2)
    notification_channels: Sequence[str] = ("email", "sms", "portal")


__all__ = ["ClaimsAppConfig"]
