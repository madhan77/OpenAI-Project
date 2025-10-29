"""Mock CRM integration connectors used for demos and tests."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional


class CRMIntegrationError(RuntimeError):
    """Raised when CRM operations cannot be completed."""


@dataclass
class CRMRecord:
    record_id: str
    url: str
    metadata: Dict[str, str] = field(default_factory=dict)


class MockZendeskClient:
    """In-memory ticketing surface with canned records."""

    def __init__(self) -> None:
        self._tickets: Dict[str, CRMRecord] = {
            "1001": CRMRecord(
                record_id="1001",
                url="https://mock.zendesk.com/tickets/1001",
                metadata={"status": "open", "subject": "Where is my order?"},
            )
        }

    async def create_ticket(self, subject: str, body: str, *, requester_email: str) -> CRMRecord:
        ticket_id = str(len(self._tickets) + 1001)
        record = CRMRecord(
            record_id=ticket_id,
            url=f"https://mock.zendesk.com/tickets/{ticket_id}",
            metadata={"status": "open", "subject": subject, "requester": requester_email},
        )
        self._tickets[ticket_id] = record
        return record

    async def update_ticket(
        self, ticket_id: str, *, status: str, comment: Optional[str] = None
    ) -> CRMRecord:
        record = self._tickets.get(ticket_id)
        if record is None:
            raise CRMIntegrationError("Ticket not found")
        record.metadata["status"] = status
        if comment:
            record.metadata["comment"] = comment
        return record

    async def list_tickets(self) -> List[CRMRecord]:
        return list(self._tickets.values())


class MockSalesforceClient:
    """Stores contacts and cases in dictionaries for offline testing."""

    def __init__(self) -> None:
        self._contacts: Dict[str, CRMRecord] = {}
        self._cases: Dict[str, CRMRecord] = {}

    async def upsert_contact(self, email: str, *, first_name: str, last_name: str) -> CRMRecord:
        record = CRMRecord(
            record_id=email,
            url=f"https://mock.salesforce.com/contacts/{email}",
            metadata={"first_name": first_name, "last_name": last_name, "email": email},
        )
        self._contacts[email] = record
        return record

    async def create_case(self, subject: str, description: str, *, contact_id: str) -> CRMRecord:
        case_id = f"CASE-{len(self._cases) + 1:04d}"
        record = CRMRecord(
            record_id=case_id,
            url=f"https://mock.salesforce.com/cases/{case_id}",
            metadata={
                "subject": subject,
                "description": description,
                "contact_id": contact_id,
            },
        )
        self._cases[case_id] = record
        return record

    async def list_cases(self) -> List[CRMRecord]:
        return list(self._cases.values())


__all__ = ["CRMIntegrationError", "CRMRecord", "MockSalesforceClient", "MockZendeskClient"]
