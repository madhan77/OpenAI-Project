"""Command line interface for the Enterprise Sales Agent application."""

from __future__ import annotations

import argparse
import json
import os
from getpass import getpass
from pathlib import Path
from typing import Any, Optional

from enterprise_sales_agent import (
    EnterpriseSalesAgent,
    FirebaseAuthError,
    FirebaseAuthService,
    FirebaseSession,
)

_DEFAULT_SESSION_PATH = Path.home() / ".enterprise_sales_agent" / "session.json"


def _print_payload(payload: Any) -> None:
    print(json.dumps(payload, indent=2))


def _authenticate_if_requested(args: argparse.Namespace) -> Optional[str]:
    if args.command == "login":
        return None

    token = _resolve_token(args)
    if not token:
        return None

    auth_service = FirebaseAuthService(
        credentials_path=args.firebase_credentials,
        project_id=args.firebase_project,
        use_emulator=args.use_firebase_emulator,
    )
    try:
        user = auth_service.authenticate(token)
    except FirebaseAuthError as exc:
        raise SystemExit(f"Firebase authentication failed: {exc}") from exc

    identity = user.email or user.uid
    print(f"Authenticated Firebase user: {identity}")
    return identity


def _resolve_token(args: argparse.Namespace) -> Optional[str]:
    if args.firebase_token:
        return args.firebase_token

    if getattr(args, "use_session", False):
        session = _load_session(Path(args.session_file))
        if not session:
            raise SystemExit(
                "No saved Firebase session found. Run the 'login' command first or "
                "provide --firebase-token explicitly."
            )
        if session.is_expired():
            raise SystemExit(
                "Saved Firebase session has expired. Log in again to refresh the token."
            )
        return session.id_token

    return None


def _load_session(path: Path) -> Optional[FirebaseSession]:
    if not path.exists():
        return None

    try:
        raw = json.loads(path.read_text())
    except json.JSONDecodeError as exc:
        raise SystemExit(f"Failed to read Firebase session at {path}: {exc}")

    return FirebaseSession.from_dict(raw)


def _save_session(path: Path, session: FirebaseSession) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(session.to_dict(), indent=2))


def _handle_login(args: argparse.Namespace) -> None:
    password = args.password or getpass("Firebase password: ")

    auth_service = FirebaseAuthService(
        credentials_path=args.firebase_credentials,
        project_id=args.firebase_project,
        use_emulator=args.use_firebase_emulator,
    )

    try:
        session = auth_service.sign_in_with_password(
            email=args.email,
            password=password,
            api_key=args.firebase_api_key,
        )
    except FirebaseAuthError as exc:
        raise SystemExit(f"Firebase login failed: {exc}") from exc

    identity = session.email or session.user_id
    print(f"Logged in as {identity}.")

    if args.remember:
        session_path = Path(args.session_file)
        _save_session(session_path, session)
        print(f"Saved session token to {session_path}.")

    # Optionally verify the token using the Admin SDK if available.
    if args.verify or args.firebase_credentials or os.getenv("FIREBASE_CREDENTIALS") or args.use_firebase_emulator:
        try:
            verified_user = auth_service.authenticate(session.id_token)
            verified_identity = verified_user.email or verified_user.uid
            print(f"Verified Firebase ID token for {verified_identity}.")
        except FirebaseAuthError as exc:
            print(f"Warning: Unable to verify ID token via Admin SDK: {exc}")


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
    parser.add_argument(
        "--firebase-api-key",
        help="Firebase web API key for email/password login (defaults to VITE_FIREBASE_API_KEY)",
    )
    parser.add_argument(
        "--session-file",
        default=str(_DEFAULT_SESSION_PATH),
        help=f"Path to store Firebase session tokens (default: {_DEFAULT_SESSION_PATH})",
    )
    parser.add_argument(
        "--use-session",
        action="store_true",
        help="Use the saved Firebase session token instead of --firebase-token",
    )

    subparsers = parser.add_subparsers(dest="command", required=True)

    login_parser = subparsers.add_parser("login", help="Sign in with Firebase email/password")
    login_parser.add_argument("--email", required=True, help="Firebase email address")
    login_parser.add_argument("--password", help="Firebase password (omit to prompt)")
    login_parser.add_argument(
        "--remember",
        action="store_true",
        help="Persist the Firebase session token for future CLI commands",
    )
    login_parser.add_argument(
        "--verify",
        action="store_true",
        help="Verify the issued ID token using the Firebase Admin SDK",
    )

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
    if args.command == "login":
        _handle_login(args)
        return

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
