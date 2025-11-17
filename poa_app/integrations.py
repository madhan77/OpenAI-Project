"""Lightweight integrations to simulate external tool connectivity."""
from __future__ import annotations

import json
import os
from dataclasses import asdict, dataclass, field
from typing import Any, Callable, Dict, List, Mapping, Sequence
from urllib import error, request

from .models import BacklogItem, MeetingAnalysis, SprintPlan


@dataclass(frozen=True)
class IntegrationResult:
    """Outcome of syncing data to an external system."""

    destination: str
    identifier: str
    status: str
    message: str = ""


@dataclass(frozen=True)
class SlackMessage:
    """Structured payload for Slack notifications."""

    channel: str
    text: str
    context: Dict[str, str] = field(default_factory=dict)


@dataclass(frozen=True)
class JiraIssuePayload:
    """Serialised representation of the Jira issue that was synced."""

    issue_key: str
    project_key: str
    summary: str
    description: str
    story_points: int | None
    labels: Sequence[str] = field(default_factory=tuple)


class JiraConnector:
    """Simulated Jira integration capturing pushed backlog items."""

    def __init__(
        self,
        *,
        project_key: str = "POA",
        base_url: str | None = None,
        transport: Callable[[Dict[str, Any]], None] | None = None,
    ) -> None:
        self.synced_items: List[BacklogItem] = []
        self.issue_payloads: List[JiraIssuePayload] = []
        self._project_key = project_key
        self._base_url = base_url or os.environ.get("POA_JIRA_BASE_URL")
        self._transport = transport

    def push_story(self, item: BacklogItem) -> IntegrationResult:
        payload = self._build_issue_payload(item)
        self.synced_items.append(item)
        self.issue_payloads.append(payload)
        status, detail = self._deliver(payload)
        return IntegrationResult(
            destination="jira",
            identifier=payload.issue_key,
            status=status,
            message=detail,
        )

    def _build_issue_payload(self, item: BacklogItem) -> JiraIssuePayload:
        summary = item.title
        lines = [item.story.narrative if item.story else item.title]
        if item.story and item.story.acceptance_criteria:
            lines.append("")
            lines.append("Acceptance Criteria:")
            lines.extend(f"- {criterion.statement}" for criterion in item.story.acceptance_criteria)
        if item.story and item.story.definition_of_done:
            lines.append("")
            lines.append("Definition of Done:")
            lines.extend(f"- {step}" for step in item.story.definition_of_done)
        description = "\n".join(lines).strip()
        labels = tuple(item.metrics.dependencies)
        return JiraIssuePayload(
            issue_key=item.identifier,
            project_key=self._project_key,
            summary=summary,
            description=description,
            story_points=getattr(item, "estimate_points", None),
            labels=labels,
        )

    def _deliver(self, payload: JiraIssuePayload) -> tuple[str, str]:
        serialised = asdict(payload)
        if self._transport is not None:
            try:
                self._transport(serialised)
            except Exception as exc:  # pragma: no cover - defensive path
                return "failed", f"Custom Jira transport error: {exc}"
            return "success", "Delivered via custom Jira transport."

        if not self._base_url:
            return "success", "Stored locally (no Jira base URL configured)."

        try:
            data = json.dumps({"fields": serialised}).encode("utf-8")
            url = f"{self._base_url.rstrip('/')}/rest/api/3/issue"
            req = request.Request(
                url,
                data=data,
                headers={"Content-Type": "application/json"},
            )
            with request.urlopen(req, timeout=5.0) as response:
                if 200 <= response.status < 300:
                    return "success", "Delivered via Jira API."
                body = response.read().decode("utf-8")
                return "failed", f"Jira responded with HTTP {response.status}: {body}"
        except error.URLError as exc:  # pragma: no cover - network failure path
            return "failed", f"Jira API error: {exc.reason}"


class SlackConnector:
    """Slack integration that can either mock or call a webhook."""

    def __init__(
        self,
        *,
        channel: str = "#product-ops",
        webhook_url: str | None = None,
        timeout: float = 5.0,
        transport: Callable[[Dict[str, str]], None] | None = None,
    ) -> None:
        self.channel = channel
        self._webhook_url = webhook_url or os.environ.get("POA_SLACK_WEBHOOK_URL")
        self._timeout = timeout
        self._transport = transport
        self.messages: List[SlackMessage] = []

    def post_story_sync(self, item: BacklogItem) -> IntegrationResult:
        text = f"Story {item.identifier} — {item.title} shared with engineering channel."
        return self._finalise_result(
            identifier=item.identifier,
            text=text,
            context={"type": "story"},
        )

    def post_meeting_summary(self, identifier: str, analysis: MeetingAnalysis) -> IntegrationResult:
        text = (
            f"Meeting {identifier} summary posted with "
            f"{len(analysis.action_items)} action items."
        )
        return self._finalise_result(
            identifier=identifier,
            text=text,
            context={"type": "meeting", "action_items": str(len(analysis.action_items))},
        )

    def post_sprint_plan(self, plan: SprintPlan) -> IntegrationResult:
        text = (
            "Sprint plan shared with total points "
            f"{plan.total_points}/{plan.capacity}."
        )
        return self._finalise_result(
            identifier="sprint-plan",
            text=text,
            context={"type": "sprint-plan", "capacity": str(plan.capacity)},
        )

    # Internal helpers -----------------------------------------------------
    def _finalise_result(
        self,
        *,
        identifier: str,
        text: str,
        context: Mapping[str, str],
    ) -> IntegrationResult:
        message = SlackMessage(channel=self.channel, text=text, context=dict(context))
        status, detail = self._deliver(message)
        suffix = f" [{detail}]" if detail else ""
        return IntegrationResult(
            destination="slack",
            identifier=identifier,
            status=status,
            message=f"{text}{suffix}",
        )

    def _deliver(self, message: SlackMessage) -> tuple[str, str]:
        self.messages.append(message)
        payload = self._serialize_payload(message)

        if self._transport is not None:
            try:
                self._transport(payload)
            except Exception as exc:  # pragma: no cover - defensive logging path
                return "failed", f"Custom transport error: {exc}"
            return "success", "Delivered via custom transport."

        if not self._webhook_url:
            return "success", "Stored locally (no webhook configured)."

        try:
            data = json.dumps(payload).encode("utf-8")
            req = request.Request(
                self._webhook_url,
                data=data,
                headers={"Content-Type": "application/json"},
            )
            with request.urlopen(req, timeout=self._timeout) as response:
                if 200 <= response.status < 300:
                    return "success", "Delivered via Slack webhook."
                body = response.read().decode("utf-8")
                return "failed", f"Slack responded with HTTP {response.status}: {body}"
        except error.URLError as exc:  # pragma: no cover - network failure path
            return "failed", f"Slack webhook error: {exc.reason}"

    def _serialize_payload(self, message: SlackMessage) -> Dict[str, str]:
        payload: Dict[str, str] = {"channel": message.channel, "text": message.text}
        payload.update({key: str(value) for key, value in message.context.items()})
        return payload


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
            status="success",
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
            status="success",
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
            status="success",
            message="Sprint plan stored for stakeholder review.",
        )


@dataclass
class IntegrationHub:
    """Aggregates connectors to provide high-level sync operations."""

    jira: JiraConnector = field(default_factory=JiraConnector)
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
    "SlackMessage",
    "JiraIssuePayload",
    "JiraConnector",
    "SlackConnector",
    "DocumentationPublisher",
    "IntegrationHub",
]
