"""Manufacturing products platform orchestrating product data, scheduling, and quality."""

from .models import (
    IoTMeasurement,
    ManufacturingSummary,
    OperationSchedule,
    OperationStep,
    ProductDefinition,
    ProductStatus,
    QualityAlert,
    ServiceEvent,
    SupplierInteraction,
    WorkOrder,
    WorkOrderStatus,
)
from .repositories import (
    InMemoryProductRepository,
    InMemoryQualityRepository,
    InMemoryServiceRepository,
    InMemorySupplierRepository,
    InMemoryWorkOrderRepository,
)
from .workflow import ManufacturingPlatform

__all__ = [
    "IoTMeasurement",
    "InMemoryProductRepository",
    "InMemoryQualityRepository",
    "InMemoryServiceRepository",
    "InMemorySupplierRepository",
    "InMemoryWorkOrderRepository",
    "ManufacturingPlatform",
    "ManufacturingSummary",
    "OperationSchedule",
    "OperationStep",
    "ProductDefinition",
    "ProductStatus",
    "QualityAlert",
    "ServiceEvent",
    "SupplierInteraction",
    "WorkOrder",
    "WorkOrderStatus",
]
