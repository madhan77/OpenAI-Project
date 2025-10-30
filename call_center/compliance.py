"""Compliance utilities for recording encryption, retention, and redaction."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Iterable

from cryptography.fernet import Fernet

from .config import get_config


@dataclass
class EncryptedRecording:
    interaction_id: str
    encrypted_blob: bytes
    expires_at: datetime
    location: str = "encrypted"


class ComplianceService:
    """Handles encryption and retention enforcement for recordings."""

    def __init__(self, *, key: bytes | None = None) -> None:
        self._fernet = Fernet(key or Fernet.generate_key())
        self._config = get_config()

    def encrypt_recording(
        self, interaction_id: str, payload: bytes, *, retention_days: int | None = None
    ) -> EncryptedRecording:
        expires_at = datetime.now(tz=timezone.utc) + timedelta(
            days=retention_days or self._config.recording_retention_days
        )
        token = self._fernet.encrypt(payload)
        return EncryptedRecording(
            interaction_id=interaction_id, encrypted_blob=token, expires_at=expires_at
        )

    def decrypt_recording(self, record: EncryptedRecording) -> bytes:
        return self._fernet.decrypt(record.encrypted_blob)

    @staticmethod
    def redact_transcript(transcript: str) -> str:
        """Mask credit card numbers and other PAN-like sequences."""

        masked = []
        for token in transcript.split():
            digits = [char for char in token if char.isdigit()]
            if len(digits) >= 12:
                masked.append("****" + token[-4:])
            else:
                masked.append(token)
        return " ".join(masked)

    @staticmethod
    def purge_expired(records: Iterable[EncryptedRecording]) -> list[EncryptedRecording]:
        now = datetime.now(tz=timezone.utc)
        return [record for record in records if record.expires_at > now]


__all__ = ["ComplianceService", "EncryptedRecording"]

