"""Simple rule-based conversation engine for the Enterprise Sales Agent."""

from __future__ import annotations

from typing import Dict


class ConversationEngine:
    """Routes user intents to application services."""

    def __init__(self, agent) -> None:
        self._agent = agent

    def respond(self, message: str) -> Dict:
        normalized = message.lower().strip()
        if "briefing" in normalized:
            account_name = self._extract_account(normalized)
            if not account_name:
                return {"response": "Please specify which account you need a briefing for."}
            briefing = self._agent.account_briefing(account_name)
            if not briefing:
                return {"response": f"I do not have information for account '{account_name}'."}
            return {
                "response": f"Sharing account briefing for {briefing['account']['name']}.",
                "payload": briefing,
            }
        if "prepare" in normalized and "meeting" in normalized:
            account_name = self._extract_account(normalized)
            if not account_name:
                return {"response": "Please specify which account the meeting is for."}
            plan = self._agent.prepare_meeting(account_name=account_name)
            if not plan:
                return {"response": f"I do not have an account named '{account_name}'."}
            return {
                "response": f"Drafted meeting plan for {plan['account']['name']}.",
                "payload": plan,
            }
        if "pipeline" in normalized:
            account_name = self._extract_account(normalized)
            if not account_name:
                return {"response": "Please specify the account to review the pipeline for."}
            overview = self._agent.pipeline_health(account_name)
            return {
                "response": f"Reviewed pipeline for {overview['account']['name']}.",
                "payload": overview,
            }
        return {
            "response": "I can help with account briefings, meeting prep, and pipeline reviews."
        }

    def _extract_account(self, text: str) -> str:
        trigger_words = ["for", "about", "on", "regarding"]
        for word in trigger_words:
            if word in text:
                parts = text.split(word, 1)
                if len(parts) > 1:
                    return parts[1].strip().strip("?.")
        return ""

