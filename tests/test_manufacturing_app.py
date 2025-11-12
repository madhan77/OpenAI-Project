"""Integration-style tests for the manufacturing platform workflow."""

from datetime import date, datetime, timedelta

from manufacturing_app import (
    ManufacturingPlatform,
    OperationStep,
    ProductDefinition,
    ProductStatus,
)


def _sample_routing() -> list[OperationStep]:
    return [
        OperationStep(
            name="CNC machining",
            machine="CNC-1",
            duration=timedelta(hours=4),
            required_skill="machinist",
            instructions="Verify tooling, clamp, run program 23A",
        ),
        OperationStep(
            name="Assembly",
            machine="Assembly-Cell",
            duration=timedelta(hours=2),
            required_skill="assembler",
            instructions="Torque to spec and log serial",
        ),
    ]


def test_end_to_end_flow_tracks_kpis() -> None:
    platform = ManufacturingPlatform()
    product = ProductDefinition(
        product_id="AX-1000",
        name="Actuator",
        revision="A",
        bom=["Housing", "Rotor", "Fasteners"],
        routing=_sample_routing(),
        owner="eng_lead",
    )
    platform.register_product(product)

    released = platform.approve_and_release_product("AX-1000", ["eng_lead", "quality_mgr"])
    assert released.status is ProductStatus.RELEASED

    wo = platform.create_work_order(
        work_order_id="WO-1",
        product_id="AX-1000",
        quantity=20,
        due_date=date(2024, 6, 1),
        priority=1,
    )
    assert wo.status.name == "PLANNED"

    start_times = {
        "CNC-1": datetime(2024, 5, 20, 6, 0, 0),
        "Assembly-Cell": datetime(2024, 5, 20, 14, 0, 0),
    }
    schedule = platform.schedule_work_orders(start_times)
    assert len(schedule) == len(_sample_routing())

    platform.start_work_order("WO-1", datetime(2024, 5, 20, 6, 0, 0))
    platform.record_measurement("WO-1", "torque", value=12.5, lower_limit=12.0, upper_limit=13.0)
    platform.record_measurement("WO-1", "torque", value=13.7, lower_limit=12.0, upper_limit=13.0)
    platform.complete_work_order("WO-1", datetime(2024, 5, 21, 12, 0, 0))

    platform.log_supplier_response(
        supplier_id="S-42",
        forecast_week=22,
        acknowledged_at=datetime(2024, 5, 1, 9, 0, 0),
        responded_at=datetime(2024, 5, 1, 18, 0, 0),
        on_time_delivery=True,
        ppm=150,
    )

    platform.report_service_event(
        serial_number="AX-1000-0001",
        product_id="AX-1000",
        issue="Field vibration",
        severity="medium",
        reported_at=datetime(2024, 5, 25, 8, 0, 0),
    )

    summary = platform.generate_summary()
    assert summary.total_products == 1
    assert summary.released_products == 1
    assert summary.work_orders_by_status["completed"] == 1
    assert summary.plan_adherence == 1.0
    assert 0 < summary.first_pass_yield < 1
    assert summary.open_quality_alerts == 1
    assert summary.supplier_otif == 1.0
    assert summary.average_supplier_ack_hours == 9.0
    assert summary.open_service_events == 1

