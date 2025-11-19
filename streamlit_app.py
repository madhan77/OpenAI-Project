"""Streamlit prototype UI for the Product Owner Assist Agent.

Launch from the repo root:
  streamlit run streamlit_app.py
"""
from __future__ import annotations

import itertools
from typing import Sequence
import os
import streamlit as st
if "last_slack_response" in st.session_state:
    st.markdown("## Slack API full response (persistent debug)")
    st.json(st.session_state["last_slack_response"])

import streamlit as st

from poa_app import (
    POAssistAgent,
    ProductIdea,
    MeetingTranscript,
    SprintCapacity,
    build_preview,
    demo_preview,
)
# Optional SQLite persistence. Fall back to in-memory repos if module isn't available.
try:  # Handle environments where the module isn't on the path yet
    from poa_app.persistence_sqlite import SqliteBacklogRepository, SqliteMeetingLog
except Exception:  # pragma: no cover - defensive fallback
    SqliteBacklogRepository = None  # type: ignore[assignment]
    SqliteMeetingLog = None  # type: ignore[assignment]
try:
    # Preferred: environment-aware factory in a separate module (no need to modify base integrations)
    from poa_app.integrations_env import build_integration_hub_from_env
except Exception:
    # Fallback: import from base integrations if available, else define a minimal factory
    try:
        from poa_app.integrations import build_integration_hub_from_env  # type: ignore
    except Exception:
        from poa_app.integrations import IntegrationHub, JiraConnector, SlackConnector, DocumentationPublisher

        def build_integration_hub_from_env() -> IntegrationHub:  # type: ignore
            return IntegrationHub(jira=JiraConnector(), slack=SlackConnector(), documentation=DocumentationPublisher())


def _jira_self_check() -> tuple[str, str]:
    """Lightweight Jira connectivity check against /myself.

    Returns (status, message) where status is one of: ok, skipped, failed.
    """
    base = os.getenv("JIRA_BASE_URL")
    email = os.getenv("JIRA_EMAIL")
    token = os.getenv("JIRA_API_TOKEN")
    if not (base and email and token):
        return ("skipped", "Jira env vars not fully configured.")
    try:
        import requests  # type: ignore

        url = f"{base.rstrip('/')}/rest/api/3/myself"
        resp = requests.get(url, auth=(email, token), timeout=10)
        if 200 <= resp.status_code < 300:
            name = resp.json().get("displayName", "")
            return ("ok", f"Authenticated as {name or email}.")
        return ("failed", f"HTTP {resp.status_code}: {resp.text[:120]}")
    except Exception as e:  # pragma: no cover - runtime-only path
        return ("failed", str(e))


def _get_agent(db_path: str | None = None) -> POAssistAgent:
    # Build or return a cached agent bound to the chosen SQLite file and env integrations
    cached: POAssistAgent | None = st.session_state.get("poa_agent")
    cached_db: str | None = st.session_state.get("poa_db_path")
    if cached is not None and (db_path == cached_db):
        return cached

    # Construct repositories (SQLite-backed if path provided)
    if db_path and SqliteBacklogRepository and SqliteMeetingLog:
        backlog_repo = SqliteBacklogRepository(db_path)
        meetings_repo = SqliteMeetingLog(db_path)
    else:
        backlog_repo = None
        meetings_repo = None

    integrations = build_integration_hub_from_env()
    agent = POAssistAgent(backlog_repository=backlog_repo, meeting_log=meetings_repo, integrations=integrations)
    st.session_state.poa_agent = agent
    st.session_state.poa_db_path = db_path
    st.session_state.idea_seq = itertools.count(101)
    return agent


def _next_identifier(prefix: str = "POA") -> str:
    seq = st.session_state.get("idea_seq")
    if seq is None:
        st.session_state.idea_seq = itertools.count(101)
        seq = st.session_state.idea_seq
    return f"{prefix}-{next(seq)}"


st.set_page_config(page_title="PO Assist Agent", page_icon="🧭", layout="wide")
st.title("PO Assist Agent – Prototype")
st.caption("Capture ideas, analyze meetings, prioritize backlog, and draft a sprint plan.")
# SQLite DB file control (sidebar)
db_path = st.sidebar.text_input("SQLite DB file", value="poa_app.db")


agent = _get_agent(db_path)

# Optional seed at startup when env var is set
if os.getenv("POA_SEED_ON_START") == "1" and not st.session_state.get("seeded_on_start"):
    demo_preview(agent)
    st.session_state["seeded_on_start"] = True

with st.sidebar:
    st.header("Sprint Capacity")
    available = st.number_input("Available points", min_value=0, max_value=200, value=20)
    focus = st.slider("Focus factor", min_value=0.1, max_value=1.0, value=0.8, step=0.05)
    capacity = SprintCapacity(available_points=int(available), focus_factor=float(focus))

    st.markdown("---")
    cols = st.columns(2)
    with cols[0]:
        if st.button("Reload from SQLite", width='stretch'):
            # Recreate the agent bound to the current DB path
            st.session_state.pop("poa_agent", None)
            st.session_state.pop("poa_db_path", None)
            st.rerun()
    with cols[1]:
        if st.button("Seed demo data", width='stretch'):
            demo_preview(agent)
            st.success("Seeded demo backlog items and a meeting.")

    # Quick integrations status hint
    SLACK_BOT_TOKEN = st.secrets["SLACK_BOT_TOKEN"] if "SLACK_BOT_TOKEN" in st.secrets else None
    SLACK_CHANNEL = st.secrets["SLACK_CHANNEL"] if "SLACK_CHANNEL" in st.secrets else None
    slack_enabled = bool(SLACK_BOT_TOKEN and SLACK_CHANNEL)
    st.info(f"Slack secrets loaded: token={'yes' if SLACK_BOT_TOKEN else 'no'}, channel={'yes' if SLACK_CHANNEL else 'no'}")
    jira_enabled = all(os.getenv(k) for k in ("JIRA_BASE_URL", "JIRA_EMAIL", "JIRA_API_TOKEN", "JIRA_PROJECT_KEY"))
    st.caption(
        f"Integrations → Slack: {'real' if slack_enabled else 'simulated'} • Jira: {'real' if jira_enabled else 'simulated'}"
    )
    if db_path and not (SqliteBacklogRepository and SqliteMeetingLog):
        st.warning("SQLite module not available; using in-memory repos. Data will not persist across restarts.")

    with st.expander("Integrations diagnostics", expanded=False):
        # Show which connector modes are active based on env
        st.caption(
            f"Slack connector: {'RealSlackConnector' if slack_enabled else 'SlackConnector (simulated)'} • "
            f"Jira connector: {'RealJiraConnector' if jira_enabled else 'JiraConnector (simulated)'}"
        )

        d_cols = st.columns(2)
        with d_cols[0]:
            if st.button("Send Slack test message", width='stretch', disabled=not slack_enabled):
                # Post a minimal plan message as a connectivity check via the agent API
                from poa_app import SprintPlan  # type: ignore

                empty_plan = SprintPlan(committed_items=(), total_points=0, capacity=0)
                try:
                    from slack_sdk import WebClient
                    client = WebClient(token=SLACK_BOT_TOKEN)
                    import datetime
                    unique_text = f"Test message from POA app (Streamlit) at {datetime.datetime.now().isoformat()}"
                    response = client.chat_postMessage(channel=SLACK_CHANNEL, text=unique_text)
                    st.session_state["last_slack_response"] = response
                    st.markdown("## Slack API full response (debug)")
                    st.json(response)
                    st.write(f"Posted to channel: {SLACK_CHANNEL}")
                    st.write(f"Bot user: {response.get('message', {}).get('user', 'N/A')}")
                    if not response["ok"]:
                        st.error(f"Slack API error: {response.get('error', 'Unknown error')}")
                    else:
                        st.success(f"Slack API response: {response['ok']} — {response['message']['text']}")
                except Exception as e:
                    st.error(f"Slack test failed: {e}")
        with d_cols[1]:
            if st.button("Check Jira auth", width='stretch', disabled=not jira_enabled):
                status, msg = _jira_self_check()
                if status == "ok":
                    st.success(msg)
                elif status == "skipped":
                    st.info(msg)
                else:
                    st.error(msg)
        # Add a temporary UI for direct Slack API test (no hardcoded secrets)
        st.markdown("**Direct Slack API test (no secrets saved):**")
        slack_token = st.text_input("Slack Bot Token", type="password")
        slack_channel = st.text_input("Slack Channel ID")
        if st.button("Test Slack API with input", width='stretch'):
            from slack_sdk import WebClient
            client = WebClient(token=slack_token)
            try:
                response = client.chat_postMessage(channel=slack_channel, text="Direct code test message from POA app (Streamlit)")
                st.success(f"Slack API response: {response['ok']} — {response['message']['text']}")
            except Exception as e:
                st.error(f"Slack API test failed: {e}")

col1, col2 = st.columns(2)

with col1:
    st.subheader("Capture Idea")
    with st.form("idea_form", clear_on_submit=True):
        title = st.text_input("Title", placeholder="Roadmap heatmap")
        persona = st.text_input("Persona", value="product owner")
        goal = st.text_input("Goal", placeholder="visualize delivery confidence")
        benefit = st.text_input("Benefit", placeholder="communicate risk earlier")
        description = st.text_area("Description", height=100)
        tags = st.text_input("Tags (comma-separated)")
        constraints = st.text_area("Constraints (one per line)", height=80)
        mark_ready = st.checkbox("Mark item as ready", value=True)
        submitted = st.form_submit_button("Add to Backlog")

        if submitted:
            if not title or not goal or not benefit:
                st.warning("Title, Goal, and Benefit are required.")
            else:
                idea = ProductIdea(
                    title=title.strip(),
                    persona=persona.strip() or "product owner",
                    goal=goal.strip(),
                    benefit=benefit.strip(),
                    description=description.strip(),
                    tags=tuple(t.strip() for t in tags.split(",") if t.strip()),
                    constraints=tuple(ln.strip() for ln in constraints.splitlines() if ln.strip()),
                )
                identifier = _next_identifier()
                item = agent.capture_idea(identifier, idea)
                if mark_ready:
                    agent.update_item_status(item.identifier, "ready")
                st.success(f"Added {identifier} to backlog.")

with col2:
    st.subheader("Register Meeting")
    with st.form("meeting_form", clear_on_submit=True):
        meeting_id = st.text_input("Meeting ID", value="weekly-sync")
        attendees = st.text_input("Attendees (comma-separated)", value="PO, Eng Lead, Design")
        goals = st.text_area("Goals (one per line)")
        discussion = st.text_area("Discussion points (one per line)")
        decisions = st.text_area("Decisions (one per line)")
        open_q = st.text_area("Open questions (one per line)")
        risks = st.text_area("Risks (one per line)")
        submitted_m = st.form_submit_button("Save Meeting")

        if submitted_m:
            transcript = MeetingTranscript(
                attendees=tuple(a.strip() for a in attendees.split(",") if a.strip()),
                goals=tuple(g.strip() for g in goals.splitlines() if g.strip()),
                discussion_points=tuple(d.strip() for d in discussion.splitlines() if d.strip()),
                decisions=tuple(d.strip() for d in decisions.splitlines() if d.strip()),
                open_questions=tuple(q.strip() for q in open_q.splitlines() if q.strip()),
                risks=tuple(r.strip() for r in risks.splitlines() if r.strip()),
            )
            agent.register_meeting(meeting_id.strip() or _next_identifier("MTG"), transcript)
            st.success(f"Saved meeting '{meeting_id}'.")

st.markdown("---")

st.subheader("Prioritized Backlog")
prioritized = agent.prioritise_backlog_repository()
if not prioritized:
    st.info("No backlog yet. Capture an idea or seed demo data.")
else:
    rows = []
    for entry in prioritized:
        item = entry.item
        rows.append({
            "Rank": entry.rank,
            "ID": item.identifier,
            "Title": item.title,
            "WSJF": round(entry.score, 2),
            "Points": item.estimate_points,
            "Status": item.status,
        })
    st.dataframe(rows, width='stretch', hide_index=True)

st.subheader("Sprint Plan")
plan = agent.plan_next_sprint(capacity)
st.metric("Capacity (effective)", plan.capacity)
st.metric("Planned points", plan.total_points)
if plan.committed_items:
    plan_rows = [{
        "Rank": e.rank,
        "ID": e.item.identifier,
        "Title": e.item.title,
        "Points": e.item.estimate_points,
    } for e in plan.committed_items]
    st.table(plan_rows)
else:
    st.write("No items selected. Adjust capacity or mark items as ready.")
if plan.notes:
    st.info("\n".join(f"• {n}" for n in plan.notes))

st.markdown("---")
st.subheader("Shareable Preview (Markdown)")
preview = build_preview(agent, capacity=capacity)
st.code(preview.as_markdown(), language="markdown")

st.markdown("---")

st.subheader("Publish to Slack & Jira")

# Publish a selected backlog item to Jira (+ Slack notification) using agent integrations
prioritized_for_publish = agent.prioritise_backlog_repository()
if prioritized_for_publish:
    options = [f"{e.item.identifier} — {e.item.title}" for e in prioritized_for_publish]
    sel = st.selectbox("Backlog item to publish", options=options, index=0)
    sel_id = sel.split(" — ", 1)[0]
    col_a, col_b, col_c = st.columns(3)
    with col_a:
        if st.button("Publish selected item (Jira + Slack)", width='stretch'):
            results = agent.sync_backlog_item(sel_id, notify=True)
            for r in results:
                st.success(f"{r.destination}: {r.status} — {r.message}")
    # Announce sprint plan to Slack (+ Docs)
    with col_b:
        if st.button("Announce sprint plan", width='stretch'):
            results = agent.announce_sprint_plan(plan)
            for r in results:
                st.success(f"{r.destination}: {r.status} — {r.message}")
    # Post latest meeting summary to Slack (+ Docs)
    with col_c:
        recent = agent.recent_meetings(limit=1)
        latest_id = recent[0].identifier if recent else None
        disabled = latest_id is None
        if st.button("Post latest meeting summary", width='stretch', disabled=disabled):
            if latest_id:
                results = agent.broadcast_meeting(latest_id)
                for r in results:
                    st.success(f"{r.destination}: {r.status} — {r.message}")
else:
    st.info("No backlog items to publish yet. Seed demo data or add an idea.")