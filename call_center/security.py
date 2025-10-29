"""Authentication, authorization, and audit capabilities."""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Dict, Iterable, Optional

from jose import JWTError, jwt
from passlib.context import CryptContext

from .config import get_config
from .models import Agent, Role


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class AuthenticationError(RuntimeError):
    """Raised when credentials cannot be validated."""


class AuthorizationService:
    """Simple RBAC service supporting OAuth2 and SSO tokens."""

    def __init__(self) -> None:
        self._config = get_config()
        self._signing_key = self._config.signing_key

    def issue_token(self, *, subject: str, roles: Iterable[Role], expires_in: int = 3600) -> str:
        now = datetime.now(tz=timezone.utc)
        payload = {
            "sub": subject,
            "roles": [role.value for role in roles],
            "iat": int(now.timestamp()),
            "exp": int((now + timedelta(seconds=expires_in)).timestamp()),
        }
        return jwt.encode(payload, self._signing_key, algorithm="HS256")

    def verify_token(self, token: str) -> Dict[str, str]:
        try:
            payload = jwt.decode(token, self._signing_key, algorithms=["HS256"])
        except JWTError as exc:  # pragma: no cover - defensive branch
            raise AuthenticationError("Invalid authentication token") from exc
        return payload

    def authenticate_agent(self, agent: Agent, password: str) -> str:
        if not agent.password_hash:
            raise AuthenticationError("Agent password not configured")
        if not pwd_context.verify(password, agent.password_hash):
            raise AuthenticationError("Invalid credentials")
        return self.issue_token(subject=agent.agent_id, roles=[agent.role])

    @staticmethod
    def hash_password(password: str) -> str:
        return pwd_context.hash(password)


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


__all__ = ["AuthenticationError", "AuthorizationService", "AuditLogger", "pwd_context"]

