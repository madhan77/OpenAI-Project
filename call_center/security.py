"""Authentication, authorization, and audit capabilities."""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Dict, Iterable, Optional

from jose import JWTError, jwt

from .config import get_config
from .models import Role


class AuthenticationError(RuntimeError):
    """Raised when credentials cannot be validated."""


class AuthorizationService:
    """Firebase-backed authentication helper used by the API surface."""

    def __init__(self) -> None:
        config = get_config()
        self._project_id = config.firebase_project_id
        self._issuer = f"https://securetoken.google.com/{self._project_id}"
        self._emulator_mode = config.firebase_emulator_mode
        if self._emulator_mode:
            self._algorithm = "HS256"
            self._verify_key = config.firebase_emulator_jwt_secret
        else:
            if not config.firebase_service_account_cert:
                raise AuthenticationError(
                    "Provide CALL_CENTER_FIREBASE_SERVICE_ACCOUNT_CERT when emulator mode is disabled"
                )
            self._algorithm = "RS256"
            self._verify_key = config.firebase_service_account_cert.replace("\\n", "\n")

    def issue_token(self, *, uid: str, roles: Iterable[Role], expires_in: int = 3600) -> str:
        """Mint an emulator-friendly Firebase token for tests and demos."""

        if not self._emulator_mode:
            raise AuthenticationError("Token minting is only supported in emulator mode")

        now = datetime.now(tz=timezone.utc)
        payload: Dict[str, object] = {
            "sub": uid,
            "uid": uid,
            "iss": self._issuer,
            "aud": self._project_id,
            "iat": int(now.timestamp()),
            "exp": int((now + timedelta(seconds=expires_in)).timestamp()),
            "roles": [role.value for role in roles],
        }
        return jwt.encode(payload, self._verify_key, algorithm=self._algorithm)

    def verify_token(self, token: str) -> Dict[str, object]:
        """Validate a Firebase ID token and return the decoded claims."""

        try:
            payload = jwt.decode(
                token,
                self._verify_key,
                algorithms=[self._algorithm],
                audience=self._project_id,
            )
        except JWTError as exc:  # pragma: no cover - defensive branch
            raise AuthenticationError("Invalid Firebase ID token") from exc

        if payload.get("iss") != self._issuer:
            raise AuthenticationError("Token issuer mismatch")

        return payload


class AuditLogger:
    """Persistent audit log for compliance."""

    def __init__(self) -> None:
        self._entries: list[dict[str, str]] = []

    def log(self, *, actor: str, action: str, details: Optional[Dict[str, str]] = None) -> None:
        entry = {
            "timestamp": datetime.now(tz=timezone.utc).isoformat(),
            "actor": actor,
            "action": action,
            "details": details or {},
        }
        self._entries.append(entry)

    @property
    def entries(self) -> list[dict[str, str]]:
        return list(self._entries)


__all__ = ["AuthenticationError", "AuthorizationService", "AuditLogger"]

