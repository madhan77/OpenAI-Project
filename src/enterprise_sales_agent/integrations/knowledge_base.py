"""Simple knowledge base integration used by the Enterprise Sales Agent."""

from __future__ import annotations

from typing import Dict, List


class KnowledgeBaseClient:
    """Returns canned playbooks and enablement assets."""

    def __init__(self) -> None:
        self._playbooks: Dict[str, List[str]] = {
            "manufacturing": [
                "Highlight predictive maintenance outcomes",
                "Quantify downtime reduction using customer benchmarks",
                "Include integration architecture diagram",
            ],
            "technology": [
                "Emphasize multi-cloud governance",
                "Show roadmap for AI compliance controls",
                "Share enterprise deployment checklist",
            ],
        }
        self._objection_handlers: Dict[str, List[str]] = {
            "pricing": [
                "Reinforce total cost of ownership savings over 3 years",
                "Offer phased rollout to align with budget cycles",
            ],
            "security": [
                "Provide SOC 2 report and data residency overview",
                "Highlight customer-managed encryption keys option",
            ],
        }

    def get_playbook_steps(self, industry: str) -> List[str]:
        return self._playbooks.get(industry.lower(), [])

    def suggest_objection_handlers(self, topic: str) -> List[str]:
        return self._objection_handlers.get(topic.lower(), [])

