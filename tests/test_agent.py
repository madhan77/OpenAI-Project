"""Tests for the Enterprise Sales Agent application."""

from __future__ import annotations

import sys
from pathlib import Path
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from enterprise_sales_agent import EnterpriseSalesAgent


class EnterpriseSalesAgentTests(unittest.TestCase):
    def setUp(self) -> None:
        self.agent = EnterpriseSalesAgent()

    def test_account_briefing_contains_playbook(self) -> None:
        briefing = self.agent.account_briefing("Acme Industries")
        self.assertIsNotNone(briefing)
        assert briefing is not None
        self.assertIn("industry_playbook", briefing)
        self.assertGreater(len(briefing["industry_playbook"]), 0)

    def test_meeting_plan_includes_agenda(self) -> None:
        plan = self.agent.prepare_meeting(account_name="Globex Corporation")
        self.assertIsNotNone(plan)
        assert plan is not None
        self.assertIn("agenda", plan)
        self.assertGreater(len(plan["agenda"]), 0)

    def test_pipeline_health_recommends_actions(self) -> None:
        overview = self.agent.pipeline_health("Acme Industries")
        self.assertIn("recommended_next_actions", overview)
        self.assertGreater(len(overview["recommended_next_actions"]), 0)

    def test_task_creation_appends_task(self) -> None:
        result = self.agent.create_follow_up_task(
            account_name="Acme Industries",
            description="Share ROI benchmarks",
            owner="Jordan Blake",
            due_in_days=1,
        )
        self.assertEqual(result["related_account"], "Acme Industries")
        tasks = self.agent.list_tasks("Acme Industries")
        self.assertTrue(any(task["description"] == "Share ROI benchmarks" for task in tasks["tasks"]))

    def test_conversation_router(self) -> None:
        result = self.agent.converse("Please prepare meeting for Globex Corporation")
        self.assertIn("Drafted meeting plan", result["response"])
        self.assertIn("payload", result)


if __name__ == "__main__":
    unittest.main()

