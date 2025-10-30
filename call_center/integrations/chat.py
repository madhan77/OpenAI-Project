"""Mock chat channel integrations backed by sample data."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional


class ChatIntegrationError(RuntimeError):
    """Raised when the chat provider encounters an error."""


@dataclass
class ChatMessage:
    message_id: str
    channel: str
    customer_id: str
    body: str
    metadata: Dict[str, str] = field(default_factory=dict)


class MockWebChatGateway:
    """In-memory chat history used for the demo application."""

    def __init__(self) -> None:
        self._conversations: Dict[str, List[ChatMessage]] = {
            "conv-100": [
                ChatMessage(
                    message_id="msg-1",
                    channel="web",
                    customer_id="cust-1",
                    body="Hello, I need help with my order.",
                )
            ]
        }

    async def send_message(self, conversation_id: str, body: str) -> ChatMessage:
        message = ChatMessage(
            message_id=f"msg-{len(self._conversations.get(conversation_id, [])) + 1}",
            channel="web",
            customer_id="cust-1",
            body=body,
        )
        self._conversations.setdefault(conversation_id, []).append(message)
        return message

    async def typing_indicator(self, conversation_id: str, active: bool) -> None:
        if conversation_id not in self._conversations:
            raise ChatIntegrationError("Conversation not found")
        # Indicator is ignored for the mock implementation.

    async def history(self, conversation_id: str) -> List[ChatMessage]:
        return list(self._conversations.get(conversation_id, []))


class MockMobileMessagingGateway:
    """Stores outbound pushes in memory for inspection during tests."""

    def __init__(self) -> None:
        self._messages: Dict[str, List[Dict[str, str]]] = {}

    async def send_push(
        self, device_id: str, body: str, *, metadata: Optional[Dict[str, str]] = None
    ) -> Dict[str, str]:
        payload = {"device_id": device_id, "body": body, "metadata": metadata or {}}
        self._messages.setdefault(device_id, []).append(payload)
        return payload

    async def history(self, device_id: str) -> List[Dict[str, str]]:
        return list(self._messages.get(device_id, []))


__all__ = [
    "ChatIntegrationError",
    "ChatMessage",
    "MockMobileMessagingGateway",
    "MockWebChatGateway",
]
