"""Tests for the Firebase authentication integration."""

from __future__ import annotations

import os
from types import SimpleNamespace
from typing import Any, Dict
import unittest
from unittest.mock import patch

from enterprise_sales_agent.auth import FirebaseAuthError, FirebaseAuthService


class _FakeFirebaseModules:
    def __init__(self) -> None:
        self.admin = SimpleNamespace()
        self.admin._apps = []  # type: ignore[attr-defined]
        self.admin_initialized_args: Dict[str, Any] | None = None

        def initialize_app(credential=None, options=None, name="[DEFAULT]") -> str:
            self.admin._apps.append("app")
            self.admin_initialized_args = {"credential": credential, "options": options, "name": name}
            return "app"

        self.admin.initialize_app = initialize_app  # type: ignore[attr-defined]
        self.admin.get_app = lambda name="[DEFAULT]": "app"  # type: ignore[attr-defined]

        self.credentials = SimpleNamespace()
        self.credentials.Certificate = lambda path: {"path": path}

        self.auth = SimpleNamespace()
        self.auth.verify_id_token = lambda token, check_revoked=False: {
            "uid": "test-user",
            "email": "user@example.com",
            "name": "Test User",
            "role": "sales",
        }

    def loader(self, name: str) -> Any:
        if name == "firebase_admin":
            return self.admin
        if name == "firebase_admin.credentials":
            return self.credentials
        if name == "firebase_admin.auth":
            return self.auth
        raise ModuleNotFoundError(name)


class FirebaseAuthServiceTests(unittest.TestCase):
    def test_authenticate_returns_user_details(self) -> None:
        modules = _FakeFirebaseModules()
        service = FirebaseAuthService(
            credentials_path="/tmp/creds.json",
            project_id="demo-project",
            module_loader=modules.loader,
        )

        user = service.authenticate("token")

        self.assertEqual(user.uid, "test-user")
        self.assertEqual(user.email, "user@example.com")
        self.assertEqual(user.display_name, "Test User")
        self.assertEqual(user.claims, {"role": "sales"})
        self.assertIsNotNone(modules.admin_initialized_args)

    def test_missing_token_raises_error(self) -> None:
        service = FirebaseAuthService(module_loader=_FakeFirebaseModules().loader)
        with self.assertRaises(FirebaseAuthError):
            service.authenticate("")

    def test_sign_in_with_password_returns_session(self) -> None:
        modules = _FakeFirebaseModules()

        def fake_request(url: str, payload: Dict[str, Any]) -> Dict[str, Any]:
            self.assertIn("signInWithPassword", url)
            self.assertEqual(payload["email"], "user@example.com")
            self.assertEqual(payload["password"], "secret")
            return {
                "idToken": "abc123",
                "refreshToken": "refresh-token",
                "localId": "uid-1",
                "email": "user@example.com",
                "expiresIn": "3600",
            }

        service = FirebaseAuthService(
            module_loader=modules.loader,
            request_func=fake_request,
            time_func=lambda: 1000.0,
        )

        session = service.sign_in_with_password(
            email="user@example.com",
            password="secret",
            api_key="demo-key",
        )

        self.assertEqual(session.id_token, "abc123")
        self.assertEqual(session.refresh_token, "refresh-token")
        self.assertEqual(session.user_id, "uid-1")
        self.assertEqual(session.email, "user@example.com")
        self.assertFalse(session.is_expired(now=1200.0))

    def test_sign_in_requires_api_key(self) -> None:
        service = FirebaseAuthService(module_loader=_FakeFirebaseModules().loader)
        with patch.dict(os.environ, {}, clear=True):
            with self.assertRaises(FirebaseAuthError):
                service.sign_in_with_password(email="user@example.com", password="secret")


if __name__ == "__main__":
    unittest.main()
