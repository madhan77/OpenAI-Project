"""Lightweight integrations to simulate external tool connectivity."""
from __future__ import annotations

import os

from dataclasses import dataclass, field
from typing import List, Sequence

from .models import BacklogItem, MeetingAnalysis, SprintPlan


@dataclass(frozen=True)
class IntegrationResult:
    """Outcome of syncing data to an external system."""

    destination: str
    identifier: str
    status: str
    message: str = ""


class JiraConnector:
    """Simulated Jira integration capturing pushed backlog items. Accepts base_url for API compatibility."""

    def __init__(self, base_url: str | None = None) -> None:
        self.synced_items: List[BacklogItem] = []
        self.base_url = base_url or os.getenv("JIRA_BASE_URL")

    def push_story(self, item: BacklogItem) -> IntegrationResult:
        self.synced_items.append(item)
        return IntegrationResult(
            destination="jira",
            identifier=item.identifier,
            status="queued",
            message=f"Story synced to Jira backlog. (base_url={self.base_url})",
        )


class SlackConnector:
    """Slack integration that can either mock or call a webhook."""

    def __init__(
        self,
        channel: str = "#all-openai-project",
        webhook_url: str | None = None,
        timeout: float = 5.0,
        transport: Callable[[Dict[str, str]], None] | None = None,
    ) -> None:
        self.channel = channel
        self._webhook_url = webhook_url or os.environ.get("POA_SLACK_WEBHOOK_URL")
        print(f"[SlackConnector] Using webhook URL: {self._webhook_url}")
        self._timeout = timeout
        self._transport = transport
        self.messages = []

    def post_story_sync(self, item: BacklogItem) -> IntegrationResult:
        message = (
            f"Story {item.identifier} — {item.title} shared with engineering channel."
        )
        self.messages.append(message)
        return IntegrationResult(
            destination="slack",
            identifier=item.identifier,
            status="sent",
            message=message,
        )

    def post_meeting_summary(self, identifier: str, analysis: MeetingAnalysis) -> IntegrationResult:
        message = f"Meeting {identifier} summary posted with {len(analysis.action_items)} action items."
        self.messages.append(message)
        return IntegrationResult(
            destination="slack",
            identifier=identifier,
            status="sent",
            message=message,
        )

    def post_sprint_plan(self, plan: SprintPlan) -> IntegrationResult:
        message = (
            "Sprint plan shared with total points "
            f"{plan.total_points}/{plan.capacity}."
        )
        self.messages.append(message)
        return IntegrationResult(
            destination="slack",
            identifier="sprint-plan",
            status="sent",
            message=message,
        )


class DocumentationPublisher:
    """Simulated documentation integration storing published narratives."""

    def __init__(self) -> None:
        self.published_pages: List[str] = []

    def publish_story(self, item: BacklogItem) -> IntegrationResult:
        content = f"## {item.title}\n\n{item.story.narrative if item.story else 'Story pending refinement.'}"
        self.published_pages.append(content)
        return IntegrationResult(
            destination="notion",
            identifier=item.identifier,
            status="published",
            message="Story exported to documentation space.",
        )

    def publish_meeting(self, identifier: str, analysis: MeetingAnalysis) -> IntegrationResult:
        content = (
            f"# {identifier}\n\n{analysis.summary}\n\n"
            + "\n".join(f"- {item}" for item in analysis.action_items)
        )
        self.published_pages.append(content)
        return IntegrationResult(
            destination="notion",
            identifier=identifier,
            status="published",
            message="Meeting notes stored in documentation space.",
        )

    def publish_sprint_plan(self, plan: SprintPlan) -> IntegrationResult:
        lines = ["# Sprint Plan", ""]
        for entry in plan.committed_items:
            lines.append(
                f"- {entry.item.identifier} ({entry.item.estimate_points} pts) — {entry.item.title}"
            )
        self.published_pages.append("\n".join(lines))
        return IntegrationResult(
            destination="notion",
            identifier="sprint-plan",
            status="published",
            message="Sprint plan stored for stakeholder review.",
        )


@dataclass
class IntegrationHub:
    """Aggregates connectors to provide high-level sync operations."""

    jira: JiraConnector = field(default_factory=lambda: JiraConnector(base_url=os.getenv("JIRA_BASE_URL")))
    slack: SlackConnector = field(default_factory=SlackConnector)
    documentation: DocumentationPublisher = field(default_factory=DocumentationPublisher)

    def sync_story(self, item: BacklogItem, *, notify: bool = True) -> Sequence[IntegrationResult]:
        results = [self.jira.push_story(item)]
        if item.story:
            results.append(self.documentation.publish_story(item))
        if notify:
            results.append(self.slack.post_story_sync(item))
        return tuple(results)

    def broadcast_meeting(self, identifier: str, analysis: MeetingAnalysis) -> Sequence[IntegrationResult]:
        results = [self.documentation.publish_meeting(identifier, analysis)]
        results.append(self.slack.post_meeting_summary(identifier, analysis))
        return tuple(results)

    def announce_sprint_plan(self, plan: SprintPlan) -> Sequence[IntegrationResult]:
        results = [self.documentation.publish_sprint_plan(plan)]
        results.append(self.slack.post_sprint_plan(plan))
        return tuple(results)


__all__ = [
    "IntegrationResult",
    "JiraConnector",
    "SlackConnector",
    "DocumentationPublisher",
    "IntegrationHub",
]
