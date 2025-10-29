"""Integration connectors for external systems."""

from .chat import ChatIntegrationError, ChatMessage, MockMobileMessagingGateway, MockWebChatGateway
from .crm import CRMIntegrationError, CRMRecord, MockSalesforceClient, MockZendeskClient
from .telephony import CallSession, MockTelephonyGateway, TelephonyIntegrationError

__all__ = [
    "ChatIntegrationError",
    "ChatMessage",
    "MockMobileMessagingGateway",
    "MockWebChatGateway",
    "CRMIntegrationError",
    "CRMRecord",
    "MockSalesforceClient",
    "MockZendeskClient",
    "CallSession",
    "TelephonyIntegrationError",
    "MockTelephonyGateway",
]
