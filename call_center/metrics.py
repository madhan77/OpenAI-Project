"""Prometheus metrics for platform observability."""
from __future__ import annotations

from prometheus_client import Counter, Gauge, Histogram


interaction_duration = Histogram(
    "call_center_interaction_duration_seconds",
    "Duration of completed interactions",
    buckets=(30, 60, 120, 180, 300, 600, 900, 1200),
)

active_agents_gauge = Gauge(
    "call_center_active_agents",
    "Number of agents currently in an active state",
    labelnames=("status",),
)

queue_depth_gauge = Gauge(
    "call_center_queue_depth",
    "Number of interactions currently enqueued",
    labelnames=("queue",),
)

interaction_counter = Counter(
    "call_center_interactions_total",
    "Total count of processed interactions",
    labelnames=("channel", "status"),
)


__all__ = [
    "active_agents_gauge",
    "interaction_counter",
    "interaction_duration",
    "queue_depth_gauge",
]

