"""Core data models for the manufacturing products platform."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime, timedelta
from enum import Enum
from typing import List, Optional


class ProductStatus(str, Enum):
    """Possible lifecycle states for a product definition."""

    DRAFT = "draft"
    RELEASED = "released"


class WorkOrderStatus(str, Enum):
    """Possible states for a work order."""

    PLANNED = "planned"
    RELEASED = "released"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"


@dataclass(frozen=True)
class OperationStep:
    """Single routing step executed on a machine with skill constraints."""

    name: str
    machine: str
    duration: timedelta
    required_skill: str
    instructions: str


@dataclass
class OperationSchedule:
    """Scheduled runtime for an operation."""

    work_order_id: str
    operation: OperationStep
    start_time: datetime
    end_time: datetime


@dataclass
class ProductDefinition:
    """Represents a product's BOM, routing, and approvals."""

    product_id: str
    name: str
    revision: str
    bom: List[str]
    routing: List[OperationStep]
    owner: str
    status: ProductStatus = ProductStatus.DRAFT
    approvals: List[str] = field(default_factory=list)


@dataclass
class WorkOrder:
    """Represents a planned production order."""

    work_order_id: str
    product_id: str
    quantity: int
    due_date: date
    priority: int
    routing: List[OperationStep]
    status: WorkOrderStatus = WorkOrderStatus.PLANNED
    planned_schedule: List[OperationSchedule] = field(default_factory=list)
    actual_start: Optional[datetime] = None
    actual_end: Optional[datetime] = None

    def mark_released(self) -> None:
        self.status = WorkOrderStatus.RELEASED

    def mark_in_progress(self, timestamp: datetime) -> None:
        self.status = WorkOrderStatus.IN_PROGRESS
        self.actual_start = timestamp

    def mark_completed(self, timestamp: datetime) -> None:
        self.status = WorkOrderStatus.COMPLETED
        self.actual_end = timestamp


@dataclass
class IoTMeasurement:
    """Captured measurement tied to a work order."""

    work_order_id: str
    name: str
    value: float
    lower_limit: float
    upper_limit: float
    timestamp: datetime
    passed: bool


@dataclass
class QualityAlert:
    """Alert triggered when measurements fall out of tolerance."""

    work_order_id: str
    measurement: IoTMeasurement
    severity: str
    issue_type: str
    corrective_action: str
    opened_at: datetime
    closed_at: Optional[datetime] = None


@dataclass
class SupplierInteraction:
    """Represents collaboration touchpoints with suppliers."""

    supplier_id: str
    forecast_week: int
    acknowledged_at: datetime
    responded_at: datetime
    on_time_delivery: bool
    ppm: int

    @property
    def response_cycle_time_hours(self) -> float:
        return (self.responded_at - self.acknowledged_at).total_seconds() / 3600


@dataclass
class ServiceEvent:
    """Serialized product service record."""

    serial_number: str
    product_id: str
    issue: str
    severity: str
    reported_at: datetime
    resolved: bool = False


@dataclass
class ManufacturingSummary:
    """Aggregated KPIs for dashboards and tests."""

    total_products: int
    released_products: int
    work_orders_by_status: dict
    plan_adherence: float
    first_pass_yield: float
    open_quality_alerts: int
    supplier_otif: float
    average_supplier_ack_hours: Optional[float]
    open_service_events: int

