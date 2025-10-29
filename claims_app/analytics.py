from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from typing import Dict, Iterable, Mapping, MutableMapping, Optional


@dataclass(slots=True)
class Metric:
    name: str
    value: float
    tags: Mapping[str, str]


class MetricsCollector:
    """Captures metrics in-memory with aggregation helpers."""

    def __init__(self) -> None:
        self._metrics: list[Metric] = []
        self._counters: MutableMapping[str, float] = defaultdict(float)

    def record(self, name: str, value: float = 1.0, *, tags: Optional[Mapping[str, str]] = None) -> None:
        metric = Metric(name=name, value=value, tags=dict(tags or {}))
        self._metrics.append(metric)
        self._counters[name] += value

    def metrics(self) -> Iterable[Metric]:
        return tuple(self._metrics)

    def counter(self, name: str) -> float:
        return self._counters.get(name, 0.0)


__all__ = ["Metric", "MetricsCollector"]
