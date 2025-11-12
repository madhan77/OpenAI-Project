"""Workflow orchestration for the manufacturing platform."""

from __future__ import annotations

from datetime import date, datetime
from statistics import mean
from typing import Dict, Iterable, List, Optional

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
    count_by_status,
)


class ManufacturingPlatform:
    """Coordinates product releases, scheduling, quality, and supplier collaboration."""

    def __init__(
        self,
        products: Optional[InMemoryProductRepository] = None,
        work_orders: Optional[InMemoryWorkOrderRepository] = None,
        quality: Optional[InMemoryQualityRepository] = None,
        suppliers: Optional[InMemorySupplierRepository] = None,
        service: Optional[InMemoryServiceRepository] = None,
    ) -> None:
        self.products = products or InMemoryProductRepository()
        self.work_orders = work_orders or InMemoryWorkOrderRepository()
        self.quality = quality or InMemoryQualityRepository()
        self.suppliers = suppliers or InMemorySupplierRepository()
        self.service = service or InMemoryServiceRepository()

    # ------------------------------------------------------------------
    # Product data management
    # ------------------------------------------------------------------
    def register_product(self, definition: ProductDefinition) -> None:
        """Stores or updates a product definition in draft form."""
        self.products.upsert(definition)

    def approve_and_release_product(self, product_id: str, approvers: Iterable[str]) -> ProductDefinition:
        """Marks a product as released once two distinct approvers sign off."""
        product = self.products.get(product_id)
        unique_approvers = list(dict.fromkeys(approvers))
        product.approvals.extend(unique_approvers)
        if len(set(product.approvals)) < 2:
            raise ValueError("At least two approvers are required before release.")
        product.status = ProductStatus.RELEASED
        self.products.upsert(product)
        return product

    # ------------------------------------------------------------------
    # Work order planning and scheduling
    # ------------------------------------------------------------------
    def create_work_order(
        self,
        work_order_id: str,
        product_id: str,
        quantity: int,
        due_date: date,
        priority: int,
    ) -> WorkOrder:
        """Creates a work order from the released routing."""
        product = self.products.get(product_id)
        if product.status != ProductStatus.RELEASED:
            raise ValueError("Product must be released before creating work orders.")
        work_order = WorkOrder(
            work_order_id=work_order_id,
            product_id=product_id,
            quantity=quantity,
            due_date=due_date,
            priority=priority,
            routing=list(product.routing),
        )
        self.work_orders.add(work_order)
        return work_order

    def schedule_work_orders(self, machine_availability: Dict[str, datetime]) -> List[OperationSchedule]:
        """Assigns operations to machines using a greedy finite schedule."""
        assignments: List[OperationSchedule] = []
        machine_available = machine_availability.copy()
        for work_order in sorted(self.work_orders.list_all(), key=lambda wo: (wo.priority, wo.due_date)):
            current_finish = None
            planned_steps: List[OperationSchedule] = []
            for step in work_order.routing:
                start_time = machine_available.get(step.machine, datetime.utcnow())
                if current_finish and start_time < current_finish:
                    start_time = current_finish
                end_time = start_time + step.duration
                machine_available[step.machine] = end_time
                current_finish = end_time
                schedule = OperationSchedule(
                    work_order_id=work_order.work_order_id,
                    operation=step,
                    start_time=start_time,
                    end_time=end_time,
                )
                assignments.append(schedule)
                planned_steps.append(schedule)
            work_order.planned_schedule = planned_steps
            work_order.mark_released()
        return assignments

    # ------------------------------------------------------------------
    # Shop-floor execution
    # ------------------------------------------------------------------
    def start_work_order(self, work_order_id: str, timestamp: datetime) -> WorkOrder:
        work_order = self.work_orders.get(work_order_id)
        work_order.mark_in_progress(timestamp)
        return work_order

    def complete_work_order(self, work_order_id: str, timestamp: datetime) -> WorkOrder:
        work_order = self.work_orders.get(work_order_id)
        work_order.mark_completed(timestamp)
        return work_order

    # ------------------------------------------------------------------
    # Quality management
    # ------------------------------------------------------------------
    def record_measurement(
        self,
        work_order_id: str,
        measurement_name: str,
        value: float,
        lower_limit: float,
        upper_limit: float,
        timestamp: Optional[datetime] = None,
    ) -> IoTMeasurement:
        timestamp = timestamp or datetime.utcnow()
        passed = lower_limit <= value <= upper_limit
        measurement = IoTMeasurement(
            work_order_id=work_order_id,
            name=measurement_name,
            value=value,
            lower_limit=lower_limit,
            upper_limit=upper_limit,
            timestamp=timestamp,
            passed=passed,
        )
        self.quality.record_measurement(measurement)
        if not passed:
            alert = QualityAlert(
                work_order_id=work_order_id,
                measurement=measurement,
                severity="high" if abs(value - upper_limit) > 0.2 * (upper_limit - lower_limit) else "medium",
                issue_type="spc_out_of_control",
                corrective_action="pause_and_investigate",
                opened_at=timestamp,
            )
            self.quality.log_alert(alert)
        return measurement

    # ------------------------------------------------------------------
    # Supplier collaboration
    # ------------------------------------------------------------------
    def log_supplier_response(
        self,
        supplier_id: str,
        forecast_week: int,
        acknowledged_at: datetime,
        responded_at: datetime,
        on_time_delivery: bool,
        ppm: int,
    ) -> SupplierInteraction:
        interaction = SupplierInteraction(
            supplier_id=supplier_id,
            forecast_week=forecast_week,
            acknowledged_at=acknowledged_at,
            responded_at=responded_at,
            on_time_delivery=on_time_delivery,
            ppm=ppm,
        )
        self.suppliers.log_interaction(interaction)
        return interaction

    # ------------------------------------------------------------------
    # Aftermarket service
    # ------------------------------------------------------------------
    def report_service_event(
        self,
        serial_number: str,
        product_id: str,
        issue: str,
        severity: str,
        reported_at: Optional[datetime] = None,
    ) -> ServiceEvent:
        reported_at = reported_at or datetime.utcnow()
        event = ServiceEvent(
            serial_number=serial_number,
            product_id=product_id,
            issue=issue,
            severity=severity,
            reported_at=reported_at,
        )
        self.service.report_event(event)
        return event

    # ------------------------------------------------------------------
    def resolve_service_event(self, serial_number: str) -> None:
        self.service.resolve_event(serial_number)

    # ------------------------------------------------------------------
    # Analytics & reporting
    # ------------------------------------------------------------------
    def generate_summary(self) -> ManufacturingSummary:
        products = self.products.list_all()
        work_orders = self.work_orders.list_all()
        measurements = list(self.quality.measurements)
        alerts = list(self.quality.alerts)
        supplier_interactions = list(self.suppliers.interactions())
        open_service = self.service.open_events()

        completed = [wo for wo in work_orders if wo.status == WorkOrderStatus.COMPLETED]
        on_time = [wo for wo in completed if wo.actual_end and wo.actual_end.date() <= wo.due_date]
        plan_adherence = len(on_time) / len(completed) if completed else 0.0

        passes = [m for m in measurements if m.passed]
        first_pass_yield = len(passes) / len(measurements) if measurements else 1.0

        otif = (
            sum(1 for i in supplier_interactions if i.on_time_delivery) / len(supplier_interactions)
            if supplier_interactions
            else 0.0
        )
        avg_ack = (
            mean(i.response_cycle_time_hours for i in supplier_interactions)
            if supplier_interactions
            else None
        )

        return ManufacturingSummary(
            total_products=len(products),
            released_products=sum(1 for p in products if p.status == ProductStatus.RELEASED),
            work_orders_by_status=count_by_status(work_orders),
            plan_adherence=plan_adherence,
            first_pass_yield=first_pass_yield,
            open_quality_alerts=len(alerts),
            supplier_otif=otif,
            average_supplier_ack_hours=avg_ack,
            open_service_events=len(open_service),
        )

