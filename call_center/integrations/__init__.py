"""Integration connectors for external systems."""

from .chat import ChatIntegrationError, ChatMessage, MobileMessagingGateway, WebChatGateway
from .crm import CRMIntegrationError, CRMRecord, SalesforceClient, ZendeskClient
from .telephony import CallSession, TelephonyIntegrationError, TwilioVoiceGateway

__all__ = [
    "ChatIntegrationError",
    "ChatMessage",
    "MobileMessagingGateway",
    "WebChatGateway",
    "CRMIntegrationError",
    "CRMRecord",
    "SalesforceClient",
    "ZendeskClient",
    "CallSession",
    "TelephonyIntegrationError",
    "TwilioVoiceGateway",
]
