"""Authentication helpers for the Enterprise Sales Agent."""

from .firebase import (
    AuthenticatedUser,
    FirebaseAuthError,
    FirebaseAuthService,
    FirebaseSession,
)

__all__ = [
    "AuthenticatedUser",
    "FirebaseAuthError",
    "FirebaseAuthService",
    "FirebaseSession",
]
