"""CRM integration connectors."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Optional

import httpx


class CRMIntegrationError(RuntimeError):
    """Raised when CRM operations cannot be completed."""


@dataclass
class CRMRecord:
    record_id: str
    url: str
    metadata: Dict[str, Any]


class ZendeskClient:
    """Minimal Zendesk Support API wrapper."""

    def __init__(self, *, subdomain: str, email: str, api_token: str, client: Optional[httpx.AsyncClient] = None) -> None:
        auth = httpx.BasicAuth(f"{email}/token", api_token)
        base_url = f"https://{subdomain}.zendesk.com/api/v2"
        self._client = client or httpx.AsyncClient(base_url=base_url, auth=auth)

    async def create_ticket(self, subject: str, body: str, *, requester_email: str) -> CRMRecord:
        payload = {
            "ticket": {
                "subject": subject,
                "comment": {"body": body},
                "requester": {"email": requester_email},
            }
        }
        response = await self._client.post("/tickets.json", json=payload)
        response.raise_for_status()
        data = response.json()["ticket"]
        return CRMRecord(record_id=str(data["id"]), url=data["url"], metadata=data)

    async def update_ticket(self, ticket_id: str, *, status: str, comment: Optional[str] = None) -> CRMRecord:
        payload = {"ticket": {"status": status}}
        if comment:
            payload["ticket"]["comment"] = {"body": comment}
        response = await self._client.put(f"/tickets/{ticket_id}.json", json=payload)
        response.raise_for_status()
        data = response.json()["ticket"]
        return CRMRecord(record_id=str(data["id"]), url=data["url"], metadata=data)

    async def close(self) -> None:
        await self._client.aclose()


class SalesforceClient:
    """Minimal Salesforce REST API wrapper using OAuth refresh flow."""

    def __init__(
        self,
        *,
        instance_url: str,
        client_id: str,
        client_secret: str,
        refresh_token: str,
        client: Optional[httpx.AsyncClient] = None,
    ) -> None:
        self._instance_url = instance_url.rstrip("/")
        self._client_id = client_id
        self._client_secret = client_secret
        self._refresh_token = refresh_token
        self._client = client or httpx.AsyncClient()
        self._access_token: Optional[str] = None

    async def _ensure_token(self) -> None:
        if self._access_token:
            return
        payload = {
            "grant_type": "refresh_token",
            "client_id": self._client_id,
            "client_secret": self._client_secret,
            "refresh_token": self._refresh_token,
        }
        response = await self._client.post(f"{self._instance_url}/services/oauth2/token", data=payload)
        response.raise_for_status()
        self._access_token = response.json()["access_token"]

    async def _headers(self) -> Dict[str, str]:
        await self._ensure_token()
        return {"Authorization": f"Bearer {self._access_token}", "Content-Type": "application/json"}

    async def upsert_contact(self, email: str, *, first_name: str, last_name: str) -> CRMRecord:
        headers = await self._headers()
        payload = {
            "FirstName": first_name,
            "LastName": last_name,
            "Email": email,
        }
        response = await self._client.patch(
            f"{self._instance_url}/services/data/v58.0/sobjects/Contact/{email}",
            headers=headers,
            json=payload,
        )
        response.raise_for_status()
        location = response.headers.get("Location") or ""
        return CRMRecord(record_id=email, url=location, metadata=payload)

    async def create_case(self, subject: str, description: str, *, contact_id: str) -> CRMRecord:
        headers = await self._headers()
        payload = {
            "Subject": subject,
            "Description": description,
            "ContactId": contact_id,
        }
        response = await self._client.post(
            f"{self._instance_url}/services/data/v58.0/sobjects/Case",
            headers=headers,
            json=payload,
        )
        response.raise_for_status()
        data = response.json()
        url = f"{self._instance_url}/lightning/r/Case/{data['id']}/view"
        return CRMRecord(record_id=data["id"], url=url, metadata=payload)

    async def close(self) -> None:
        await self._client.aclose()


__all__ = ["CRMIntegrationError", "CRMRecord", "SalesforceClient", "ZendeskClient"]

