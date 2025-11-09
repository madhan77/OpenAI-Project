"""Firebase authentication integration for the Enterprise Sales Agent."""

from __future__ import annotations

import json
import os
import time
from dataclasses import dataclass, field
from importlib import import_module
from types import ModuleType
from typing import Any, Callable, Dict, Optional
from urllib import error, request


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
        request_func: Callable[[str, Dict[str, Any]], Dict[str, Any]] | None = None,
        time_func: Callable[[], float] | None = None,
    ) -> None:
        self._credentials_path = credentials_path or os.getenv("FIREBASE_CREDENTIALS")
        self._project_id = project_id or os.getenv("FIREBASE_PROJECT_ID")
        self._use_emulator = use_emulator or bool(os.getenv("FIREBASE_AUTH_EMULATOR_HOST"))
        self._module_loader = module_loader or import_module
        self._request_func = request_func or self._default_request
        self._time_func = time_func or time.time

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

    def sign_in_with_password(
        self,
        *,
        email: str,
        password: str,
        api_key: Optional[str] = None,
    ) -> "FirebaseSession":
        """Authenticate with Firebase using an email/password credential.

        This method relies on the Firebase Identity Toolkit REST API, making it
        usable without the Admin SDK installed. The resulting ID token can be
        reused with :meth:`authenticate` for server-side verification when the
        Admin SDK is available.
        """

        if not email or not password:
            raise FirebaseAuthError("Both email and password are required to sign in with Firebase.")

        web_api_key = (
            api_key
            or os.getenv("FIREBASE_WEB_API_KEY")
            or os.getenv("VITE_FIREBASE_API_KEY")
        )
        if not web_api_key:
            raise FirebaseAuthError(
                "A Firebase web API key is required. Pass api_key explicitly or set "
                "FIREBASE_WEB_API_KEY/VITE_FIREBASE_API_KEY."
            )

        url = (
            "https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key="
            f"{web_api_key}"
        )
        payload = {
            "email": email,
            "password": password,
            "returnSecureToken": True,
        }

        response = self._request_func(url, payload)

        try:
            expires_in = int(response.get("expiresIn", "0"))
        except (TypeError, ValueError):  # pragma: no cover - defensive
            expires_in = 0

        return FirebaseSession(
            id_token=response.get("idToken", ""),
            refresh_token=response.get("refreshToken"),
            user_id=response.get("localId", ""),
            email=response.get("email"),
            expires_at=self._time_func() + expires_in if expires_in else self._time_func(),
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

    def _default_request(self, url: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        data = json.dumps(payload).encode("utf-8")
        http_request = request.Request(
            url,
            data=data,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        try:
            with request.urlopen(http_request, timeout=10) as response:
                body = response.read().decode("utf-8")
        except error.HTTPError as exc:  # pragma: no cover - depends on network
            message = self._extract_error_message(exc)
            raise FirebaseAuthError(f"Firebase login failed: {message}") from exc
        except error.URLError as exc:  # pragma: no cover - depends on network
            raise FirebaseAuthError(f"Failed to contact Firebase: {exc.reason}") from exc

        try:
            return json.loads(body)
        except json.JSONDecodeError as exc:  # pragma: no cover - depends on network
            raise FirebaseAuthError("Unexpected response from Firebase Authentication.") from exc

    def _extract_error_message(self, http_error: error.HTTPError) -> str:
        try:
            details = json.loads(http_error.read().decode("utf-8"))
        except Exception:  # pragma: no cover - defensive
            return http_error.reason

        if isinstance(details, dict):
            error_info = details.get("error")
            if isinstance(error_info, dict):
                return error_info.get("message", http_error.reason)
        return http_error.reason


@dataclass
class FirebaseSession:
    """Represents a Firebase authenticated session token."""

    id_token: str
    refresh_token: Optional[str]
    user_id: str
    email: Optional[str]
    expires_at: float

    def is_expired(self, *, margin_seconds: int = 30, now: Optional[float] = None) -> bool:
        current_time = now if now is not None else time.time()
        return current_time >= (self.expires_at - margin_seconds)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id_token": self.id_token,
            "refresh_token": self.refresh_token,
            "user_id": self.user_id,
            "email": self.email,
            "expires_at": self.expires_at,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "FirebaseSession":
        return cls(
            id_token=data.get("id_token", ""),
            refresh_token=data.get("refresh_token"),
            user_id=data.get("user_id", ""),
            email=data.get("email"),
            expires_at=float(data.get("expires_at", 0)),
        )

