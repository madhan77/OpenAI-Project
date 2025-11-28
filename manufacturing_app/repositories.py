"""In-memory repositories for the manufacturing platform."""

from __future__ import annotations

from collections import defaultdict
from typing import Dict, Iterable, List

from .models import (
    IoTMeasurement,
    ProductDefinition,
    QualityAlert,
    ServiceEvent,
    SupplierInteraction,
    WorkOrder,
    WorkOrderStatus,
)


class InMemoryProductRepository:
    """Stores product definitions for quick lookup."""

    def __init__(self) -> None:
        self._products: Dict[str, ProductDefinition] = {}

    def upsert(self, product: ProductDefinition) -> None:
        self._products[product.product_id] = product

    def get(self, product_id: str) -> ProductDefinition:
        return self._products[product_id]

    def list_all(self) -> List[ProductDefinition]:
        return list(self._products.values())


class InMemoryWorkOrderRepository:
    """Tracks work orders and their lifecycle."""

    def __init__(self) -> None:
        self._work_orders: Dict[str, WorkOrder] = {}

    def add(self, work_order: WorkOrder) -> None:
        self._work_orders[work_order.work_order_id] = work_order

    def get(self, work_order_id: str) -> WorkOrder:
        return self._work_orders[work_order_id]

    def list_all(self) -> List[WorkOrder]:
        return list(self._work_orders.values())

    def list_by_status(self, status: WorkOrderStatus) -> List[WorkOrder]:
        return [wo for wo in self._work_orders.values() if wo.status == status]


class InMemoryQualityRepository:
    """Stores IoT measurements and alerts."""

    def __init__(self) -> None:
        self._measurements: List[IoTMeasurement] = []
        self._alerts: List[QualityAlert] = []

    def record_measurement(self, measurement: IoTMeasurement) -> None:
        self._measurements.append(measurement)

    def log_alert(self, alert: QualityAlert) -> None:
        self._alerts.append(alert)

    @property
    def measurements(self) -> Iterable[IoTMeasurement]:
        return tuple(self._measurements)

    @property
    def alerts(self) -> Iterable[QualityAlert]:
        return tuple(self._alerts)


class InMemorySupplierRepository:
    """Captures supplier interactions to derive KPIs."""

    def __init__(self) -> None:
        self._interactions: List[SupplierInteraction] = []

    def log_interaction(self, interaction: SupplierInteraction) -> None:
        self._interactions.append(interaction)

    def interactions(self) -> Iterable[SupplierInteraction]:
        return tuple(self._interactions)


class InMemoryServiceRepository:
    """Records aftermarket service events."""

    def __init__(self) -> None:
        self._events: Dict[str, ServiceEvent] = {}

    def report_event(self, event: ServiceEvent) -> None:
        self._events[event.serial_number] = event

    def resolve_event(self, serial_number: str) -> None:
        if serial_number in self._events:
            self._events[serial_number].resolved = True

    def open_events(self) -> List[ServiceEvent]:
        return [event for event in self._events.values() if not event.resolved]

    def all_events(self) -> List[ServiceEvent]:
        return list(self._events.values())


def count_by_status(work_orders: Iterable[WorkOrder]) -> Dict[str, int]:
    """Utility for summarising work orders per status."""

    counts: Dict[str, int] = defaultdict(int)
    for order in work_orders:
        counts[order.status.value] += 1
    return dict(counts)

