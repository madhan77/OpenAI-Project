"""Natural language ingestion helpers for the PO Assist Agent."""
from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Iterable, List, Sequence

from .models import MeetingTranscript, ProductIdea

_STORY_PATTERN = re.compile(
    r"as a (?P<persona>.+?),? i want (?P<goal>.+?) so that (?P<benefit>.+?)(?:\.|$)",
    re.IGNORECASE,
)


@dataclass(frozen=True)
class ParsedIdea:
    """Result of parsing a free-form product idea."""

    idea: ProductIdea
    notes: Sequence[str] = ()


def _normalise_lines(text: str) -> List[str]:
    return [line.strip() for line in text.splitlines() if line.strip()]


def _extract_list(lines: Sequence[str], *labels: str) -> List[str]:
    values: List[str] = []
    current: str | None = None
    label_set = {label.lower() for label in labels}

    for line in lines:
        if ":" in line:
            prefix, remainder = line.split(":", 1)
            if prefix.strip().lower() in label_set:
                current = prefix.strip().lower()
                remainder = remainder.strip()
                if remainder:
                    values.extend(_split_list_value(remainder))
                continue
            current = None
            continue

        if current and line and line[0] in "-•*":
            values.append(line[1:].strip())
        elif current and line:
            values.extend(_split_list_value(line))
        else:
            current = None

    return values


def _split_list_value(value: str) -> List[str]:
    parts = [segment.strip() for segment in re.split(r"[,;/]", value)]
    return [segment for segment in parts if segment]


def parse_product_idea(text: str) -> ParsedIdea:
    """Convert a free-form description into a `ProductIdea`."""

    lines = _normalise_lines(text)
    combined = " ".join(lines)
    notes: List[str] = []

    persona = "product owner"
    goal = "deliver outcomes"
    benefit = "stakeholders remain aligned"

    match = _STORY_PATTERN.search(combined)
    if match:
        persona = match.group("persona").strip()
        goal = match.group("goal").strip()
        benefit = match.group("benefit").strip()
        notes.append("Derived story narrative from natural language input.")

    def _extract_numeric(label: str) -> int | None:
        pattern = re.compile(rf"{label}\s*[:=]\s*(\d+)", re.IGNORECASE)
        found = pattern.search(combined)
        if found:
            return int(found.group(1))
        return None

    title = next(
        (
            line.split(":", 1)[1].strip()
            for line in lines
            if line.lower().startswith("title:")
        ),
        None,
    )
    if not title and lines:
        title = lines[0][:80]

    description = " ".join(lines[1:]) if len(lines) > 1 else text.strip()

    constraints = tuple(_extract_list(lines, "constraints", "requirements", "must"))
    tags = tuple(
        tag.lstrip("#").lower()
        for tag in _extract_list(lines, "tags", "labels")
    )

    impact = _extract_numeric("impact")
    urgency = _extract_numeric("urgency")
    risk_mitigation = _extract_numeric("risk")
    estimated_effort = _extract_numeric("effort")

    product_idea = ProductIdea(
        title=title or "Untitled Idea",
        persona=persona,
        goal=goal,
        benefit=benefit,
        description=description,
        constraints=constraints,
        tags=tags,
        impact=impact,
        urgency=urgency,
        risk_mitigation=risk_mitigation,
        estimated_effort=estimated_effort,
    )

    return ParsedIdea(idea=product_idea, notes=tuple(notes))


def parse_meeting_notes(text: str) -> MeetingTranscript:
    """Extract a meeting transcript structure from notes or call summaries."""

    lines = _normalise_lines(text)
    sections = {
        "attendees": _extract_list(lines, "attendees", "participants"),
        "goals": _extract_list(lines, "goals", "objectives", "agenda"),
        "discussion_points": _extract_list(lines, "discussion", "notes", "highlights"),
        "decisions": _extract_list(lines, "decisions", "outcomes"),
        "open_questions": _extract_list(lines, "questions", "follow ups"),
        "risks": _extract_list(lines, "risks", "concerns"),
    }

    if not sections["attendees"] and lines:
        sections["attendees"] = _split_list_value(lines[0])

    if not sections["discussion_points"]:
        sections["discussion_points"] = lines[1:3]

    return MeetingTranscript(
        attendees=tuple(sections["attendees"]) or ("Product Owner", "Team"),
        goals=tuple(sections["goals"]) or ("Clarify product direction",),
        discussion_points=tuple(sections["discussion_points"]) or tuple(lines[:3]),
        decisions=tuple(sections["decisions"]),
        open_questions=tuple(sections["open_questions"]),
        risks=tuple(sections["risks"]),
    )


__all__ = ["ParsedIdea", "parse_product_idea", "parse_meeting_notes"]
