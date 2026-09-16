"""Typed runtime state views for Ayeon Core."""

from __future__ import annotations

from dataclasses import dataclass

from ayeon.contracts.common import HealthState
from ayeon.contracts.health import HealthReport
from ayeon.contracts.lifecycle import LifecycleState


@dataclass(frozen=True, slots=True)
class RuntimeStateView:
    """Immutable external view of current runtime state."""

    lifecycle: LifecycleState
    health: HealthState
    health_reports: tuple[HealthReport, ...]
    has_critical_failure: bool
