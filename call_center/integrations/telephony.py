"""Telephony integration layer for the production call center platform."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Optional

import httpx

from ..config import get_config


class TelephonyIntegrationError(RuntimeError):
    """Raised when the telephony provider cannot fulfil a request."""


@dataclass
class CallSession:
    """Represents the lifecycle of a call bridged through the telephony provider."""

    call_sid: str
    interaction_id: str
    queue: str
    agent_id: Optional[str] = None
    customer_number: Optional[str] = None
    recording_sid: Optional[str] = None


class TwilioVoiceGateway:
    """Thin wrapper around the Twilio REST API used by the call center platform."""

    def __init__(self, *, client: Optional[httpx.AsyncClient] = None) -> None:
        config = get_config()
        if not config.twilio_account_sid or not config.twilio_auth_token:
            raise TelephonyIntegrationError(
                "Twilio credentials are not configured; set CALL_CENTER_TWILIO_ACCOUNT_SID and CALL_CENTER_TWILIO_AUTH_TOKEN."
            )

        self._account_sid = config.twilio_account_sid
        self._auth = (config.twilio_account_sid, config.twilio_auth_token)
        base_url = str(config.twilio_base_url or "https://api.twilio.com/2010-04-01")
        self._client = client or httpx.AsyncClient(base_url=base_url, auth=self._auth)

    async def initiate_call(self, from_number: str, to_number: str, *, interaction_id: str) -> CallSession:
        """Initiate an outbound call through Twilio."""

        payload = {
            "From": from_number,
            "To": to_number,
            "Url": "https://handler.call-center.local/voice/ivr",
        }
        response = await self._client.post(f"/Accounts/{self._account_sid}/Calls.json", data=payload)
        response.raise_for_status()
        data = response.json()
        return CallSession(call_sid=data["sid"], interaction_id=interaction_id, queue="outbound")

    async def bridge_agent(self, call_sid: str, agent_number: str) -> None:
        """Connect an available agent to the call via TwiML instructions."""

        payload = {"Url": "https://handler.call-center.local/voice/connect", "Method": "POST"}
        response = await self._client.post(
            f"/Accounts/{self._account_sid}/Calls/{call_sid}.json", data=payload
        )
        response.raise_for_status()

    async def fetch_recording(self, recording_sid: str) -> bytes:
        """Download a call recording for compliance review."""

        response = await self._client.get(
            f"/Accounts/{self._account_sid}/Recordings/{recording_sid}.mp3"
        )
        response.raise_for_status()
        return response.content

    async def update_call_metadata(self, call_sid: str, *, metadata: Dict[str, Any]) -> None:
        """Attach custom metadata to a call via Twilio's Call Updates API."""

        payload = {f"Twilio-Call-Data-{key}": value for key, value in metadata.items()}
        response = await self._client.post(
            f"/Accounts/{self._account_sid}/Calls/{call_sid}.json", data=payload
        )
        response.raise_for_status()

    async def close(self) -> None:
        await self._client.aclose()


__all__ = ["TwilioVoiceGateway", "TelephonyIntegrationError", "CallSession"]

