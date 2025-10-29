"""Pipeline management and forecasting helpers."""

from __future__ import annotations

from dataclasses import asdict
from statistics import mean
from typing import Dict, List

from ..integrations.crm import CRMClient


class PipelineManagementService:
    """Analyzes opportunities and proposes next actions."""

    def __init__(self, crm: CRMClient) -> None:
        self._crm = crm

    def pipeline_health(self, account_name: str) -> Dict:
        account = self._crm.find_account_by_name(account_name)
        if not account:
            raise ValueError(f"Unknown account: {account_name}")

        flagged_opportunities = [
            opportunity
            for opportunity in account.opportunities
            if opportunity.health_score < 70 or "risk" in " ".join(opportunity.risks).lower()
        ]

        return {
            "account": self._crm.serialize_account(account),
            "flagged_opportunities": [asdict(opportunity) for opportunity in flagged_opportunities],
            "forecast": self._forecast_for_account(account.name),
            "recommended_next_actions": self._recommend_actions(flagged_opportunities),
        }

    def org_wide_forecast(self) -> Dict:
        totals: List[float] = []
        per_account: Dict[str, float] = {}
        for account in self._crm.list_accounts():
            amount = sum(opportunity.amount for opportunity in account.opportunities)
            totals.append(amount)
            per_account[account.name] = amount
        avg_deal_size = mean(totals) / max(len(totals), 1)
        return {
            "total_pipeline": sum(totals),
            "average_deal_size": round(avg_deal_size, 2),
            "per_account_totals": per_account,
        }

    def _forecast_for_account(self, account_name: str) -> Dict:
        account = self._crm.find_account_by_name(account_name)
        if not account:
            raise ValueError(f"Unknown account: {account_name}")

        weighted_pipeline = 0.0
        stage_weights = {
            "prospecting": 0.1,
            "qualification": 0.2,
            "value proposition": 0.35,
            "proposal/price quote": 0.55,
            "negotiation/review": 0.8,
            "closed won": 1.0,
        }
        for opportunity in account.opportunities:
            weight = stage_weights.get(opportunity.stage.lower(), 0.3)
            weighted_pipeline += opportunity.amount * weight

        return {
            "weighted_pipeline": round(weighted_pipeline, 2),
            "open_opportunities": len(account.opportunities),
        }

    def _recommend_actions(self, opportunities: List) -> List[str]:
        if not opportunities:
            return ["Maintain regular cadence and update forecast next week."]

        actions = []
        for opportunity in opportunities:
            base = f"Opportunity {opportunity.id} ({opportunity.name})"
            if opportunity.health_score < 60:
                actions.append(f"{base}: schedule executive sponsor call to address concerns.")
            if any("security" in risk.lower() for risk in opportunity.risks):
                actions.append(f"{base}: involve security specialist to mitigate risk.")
            if any("budget" in risk.lower() for risk in opportunity.risks):
                actions.append(f"{base}: align with finance on budget confirmation.")
            if not actions:
                actions.append(f"{base}: reinforce value with ROI benchmarks.")
        return actions

