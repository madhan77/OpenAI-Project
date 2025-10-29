"""Command line interface for the Enterprise Sales Agent application."""

from __future__ import annotations

import argparse
import json
from typing import Any, Optional

from enterprise_sales_agent import EnterpriseSalesAgent, FirebaseAuthError, FirebaseAuthService


def _print_payload(payload: Any) -> None:
    print(json.dumps(payload, indent=2))


def _authenticate_if_requested(args: argparse.Namespace) -> Optional[str]:
    if not args.firebase_token:
        return None

    auth_service = FirebaseAuthService(
        credentials_path=args.firebase_credentials,
        project_id=args.firebase_project,
        use_emulator=args.use_firebase_emulator,
    )
    try:
        user = auth_service.authenticate(args.firebase_token)
    except FirebaseAuthError as exc:
        raise SystemExit(f"Firebase authentication failed: {exc}") from exc

    identity = user.email or user.uid
    print(f"Authenticated Firebase user: {identity}")
    return identity


def main() -> None:
    parser = argparse.ArgumentParser(description="Enterprise Sales Agent CLI")
    parser.add_argument("--firebase-token", help="Firebase ID token to authenticate requests")
    parser.add_argument(
        "--firebase-credentials",
        help="Path to Firebase service account JSON used to verify ID tokens",
    )
    parser.add_argument("--firebase-project", help="Firebase project ID")
    parser.add_argument(
        "--use-firebase-emulator",
        action="store_true",
        help="Use the Firebase Authentication emulator (credentials optional)",
    )

    subparsers = parser.add_subparsers(dest="command", required=True)

    briefing_parser = subparsers.add_parser("briefing", help="Generate account briefing")
    briefing_parser.add_argument("account", help="Account name, e.g. 'Acme Industries'")

    meeting_parser = subparsers.add_parser("meeting", help="Prepare meeting plan")
    meeting_parser.add_argument("account", help="Account name")

    pipeline_parser = subparsers.add_parser(
        "pipeline", help="Review pipeline health and recommendations"
    )
    pipeline_parser.add_argument("account", help="Account name")

    task_parser = subparsers.add_parser("task", help="Create a follow-up task")
    task_parser.add_argument("account", help="Account name")
    task_parser.add_argument("owner", help="Task owner")
    task_parser.add_argument("description", help="Task description")
    task_parser.add_argument(
        "--due-in-days",
        type=int,
        default=2,
        help="Number of days until due date (default: 2)",
    )

    convo_parser = subparsers.add_parser("chat", help="Ask the agent a question")
    convo_parser.add_argument("message", help="Free-form message to the agent")

    args = parser.parse_args()
    _authenticate_if_requested(args)

    agent = EnterpriseSalesAgent()

    if args.command == "briefing":
        briefing = agent.account_briefing(args.account)
        if not briefing:
            print("Account not found.")
            return
        _print_payload(briefing)
    elif args.command == "meeting":
        plan = agent.prepare_meeting(account_name=args.account)
        if not plan:
            print("Account not found.")
            return
        _print_payload(plan)
    elif args.command == "pipeline":
        overview = agent.pipeline_health(args.account)
        _print_payload(overview)
    elif args.command == "task":
        task = agent.create_follow_up_task(
            account_name=args.account,
            owner=args.owner,
            description=args.description,
            due_in_days=args.due_in_days,
        )
        _print_payload(task)
    elif args.command == "chat":
        result = agent.converse(args.message)
        _print_payload(result)


if __name__ == "__main__":
    main()
