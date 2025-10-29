"""Chat channel integrations (web chat and mobile messaging)."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Optional

import httpx


class ChatIntegrationError(RuntimeError):
    """Raised when the chat provider returns an error."""


@dataclass
class ChatMessage:
    message_id: str
    channel: str
    customer_id: str
    body: str
    metadata: Dict[str, Any]


class WebChatGateway:
    """Integration against a hosted web chat provider."""

    def __init__(self, *, base_url: str, token: str, client: Optional[httpx.AsyncClient] = None) -> None:
        self._client = client or httpx.AsyncClient(base_url=base_url, headers={"Authorization": f"Bearer {token}"})

    async def send_message(self, conversation_id: str, body: str) -> ChatMessage:
        payload = {"body": body}
        response = await self._client.post(f"/conversations/{conversation_id}/messages", json=payload)
        response.raise_for_status()
        data = response.json()
        return ChatMessage(
            message_id=data["id"],
            channel="web",
            customer_id=data.get("customer_id", "unknown"),
            body=data["body"],
            metadata=data.get("metadata", {}),
        )

    async def typing_indicator(self, conversation_id: str, active: bool) -> None:
        payload = {"typing": active}
        response = await self._client.post(f"/conversations/{conversation_id}/typing", json=payload)
        response.raise_for_status()

    async def close(self) -> None:
        await self._client.aclose()


class MobileMessagingGateway:
    """Integration against a mobile push/chat provider."""

    def __init__(self, *, base_url: str, api_key: str, client: Optional[httpx.AsyncClient] = None) -> None:
        headers = {"X-API-Key": api_key}
        self._client = client or httpx.AsyncClient(base_url=base_url, headers=headers)

    async def send_push(self, device_id: str, body: str, *, metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        payload = {"device_id": device_id, "body": body, "metadata": metadata or {}}
        response = await self._client.post("/push", json=payload)
        response.raise_for_status()
        return response.json()

    async def close(self) -> None:
        await self._client.aclose()


__all__ = [
    "ChatIntegrationError",
    "ChatMessage",
    "MobileMessagingGateway",
    "WebChatGateway",
]

