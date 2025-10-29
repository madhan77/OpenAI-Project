"""Firebase authentication integration for the Enterprise Sales Agent."""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from importlib import import_module
from types import ModuleType
from typing import Any, Callable, Dict, Optional


class FirebaseAuthError(RuntimeError):
    """Raised when Firebase authentication cannot be completed."""


@dataclass
class AuthenticatedUser:
    """Represents an authenticated Firebase user."""

    uid: str
    email: Optional[str] = None
    display_name: Optional[str] = None
    claims: Dict[str, Any] = field(default_factory=dict)


class FirebaseAuthService:
    """Verify Firebase ID tokens for Enterprise Sales Agent clients.

    The service relies on the Firebase Admin SDK but defers importing it until
    authentication is required. This makes the integration optional for local
    prototyping scenarios where Firebase is not configured.
    """

    _RESERVED_CLAIMS = {
        "aud",
        "auth_time",
        "exp",
        "firebase",
        "iat",
        "iss",
        "sub",
        "uid",
        "email",
        "email_verified",
        "name",
        "picture",
    }

    def __init__(
        self,
        *,
        credentials_path: Optional[str] = None,
        project_id: Optional[str] = None,
        use_emulator: bool = False,
        module_loader: Callable[[str], ModuleType] | None = None,
    ) -> None:
        self._credentials_path = credentials_path or os.getenv("FIREBASE_CREDENTIALS")
        self._project_id = project_id or os.getenv("FIREBASE_PROJECT_ID")
        self._use_emulator = use_emulator or bool(os.getenv("FIREBASE_AUTH_EMULATOR_HOST"))
        self._module_loader = module_loader or import_module

        self._firebase_admin: Optional[ModuleType] = None
        self._credentials_module: Optional[ModuleType] = None
        self._auth_module: Optional[ModuleType] = None
        self._app: Any = None

    # Public API ---------------------------------------------------------

    def authenticate(self, id_token: str) -> AuthenticatedUser:
        """Verify the provided Firebase ID token and return user details."""

        if not id_token:
            raise FirebaseAuthError("An ID token is required for Firebase authentication.")

        auth_module = self._ensure_initialized()

        try:
            decoded_token = auth_module.verify_id_token(id_token, check_revoked=False)
        except Exception as exc:  # pragma: no cover - passthrough for SDK errors
            raise FirebaseAuthError(f"Failed to verify Firebase ID token: {exc}") from exc

        return AuthenticatedUser(
            uid=decoded_token.get("uid") or decoded_token.get("sub"),
            email=decoded_token.get("email"),
            display_name=decoded_token.get("name"),
            claims={
                key: value
                for key, value in decoded_token.items()
                if key not in self._RESERVED_CLAIMS
            },
        )

    # Internal helpers ---------------------------------------------------

    def _ensure_initialized(self) -> ModuleType:
        if self._auth_module is not None:
            return self._auth_module

        firebase_admin = self._load_module("firebase_admin")
        credentials_module = self._load_module("firebase_admin.credentials")
        auth_module = self._load_module("firebase_admin.auth")

        if firebase_admin._apps:  # type: ignore[attr-defined]
            self._app = firebase_admin.get_app()
        else:
            self._app = self._initialize_app(firebase_admin, credentials_module)

        self._firebase_admin = firebase_admin
        self._credentials_module = credentials_module
        self._auth_module = auth_module
        return auth_module

    def _initialize_app(self, firebase_admin: ModuleType, credentials_module: ModuleType) -> Any:
        options: Dict[str, Any] = {}
        if self._project_id:
            options["projectId"] = self._project_id

        if self._use_emulator:
            # When using the Firebase emulator suite, credentials are optional.
            return firebase_admin.initialize_app(options=options or None)

        if not self._credentials_path:
            raise FirebaseAuthError(
                "Firebase credentials path not provided. Set the FIREBASE_CREDENTIALS "
                "environment variable or pass credentials_path explicitly."
            )

        credential = credentials_module.Certificate(self._credentials_path)
        return firebase_admin.initialize_app(credential, options or None)

    def _load_module(self, name: str) -> ModuleType:
        try:
            return self._module_loader(name)
        except ModuleNotFoundError as exc:  # pragma: no cover - environment dependent
            raise FirebaseAuthError(
                "Firebase Admin SDK is required but not installed. Install the "
                "'firebase-admin' package to enable authentication."
            ) from exc

