"""Meeting analysis heuristics for the PO Assist Agent."""
from __future__ import annotations

from typing import List

from .models import MeetingAnalysis, MeetingTranscript


def _summarize(transcript: MeetingTranscript) -> str:
    agenda = ", ".join(transcript.goals)
    attendees = ", ".join(transcript.attendees)
    return (
        f"Session with {attendees} covering {agenda}. Key discussion points: "
        + "; ".join(transcript.discussion_points)
    )


def _derive_action_items(transcript: MeetingTranscript) -> List[str]:
    actions: List[str] = []

    for decision in transcript.decisions:
        actions.append(f"Execute follow-up for decision: {decision}")

    for question in transcript.open_questions:
        actions.append(f"Clarify open question: {question}")

    for risk in transcript.risks:
        actions.append(f"Mitigate risk: {risk}")

    return actions


def _derive_clarity_gaps(transcript: MeetingTranscript) -> List[str]:
    gaps = [
        f"Unresolved question: {question}" for question in transcript.open_questions
    ]

    if not gaps and transcript.risks:
        gaps.append("Validate mitigations for identified risks.")

    return gaps


def analyze_meeting(transcript: MeetingTranscript) -> MeetingAnalysis:
    """Create a structured summary and task list for a meeting transcript."""

    summary = _summarize(transcript)
    actions = _derive_action_items(transcript)
    clarity_gaps = _derive_clarity_gaps(transcript)

    return MeetingAnalysis(
        summary=summary,
        action_items=actions,
        clarity_gaps=clarity_gaps,
        risks=list(transcript.risks),
    )


__all__ = ["analyze_meeting"]
