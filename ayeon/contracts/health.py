"""Health contracts for Ayeon Core."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import StrEnum

from ayeon.contracts.common import HealthState, utc_now


class ComponentCriticality(StrEnum):
    """Operational importance of a runtime component."""

    OPTIONAL = "optional"
    IMPORTANT = "important"
    CRITICAL = "critical"


@dataclass(frozen=True, slots=True)
class HealthReport:
    """Immutable health observation for one runtime component."""

    component: str
    state: HealthState
    criticality: ComponentCriticality = ComponentCriticality.IMPORTANT
    reason: str | None = None
    checked_at: datetime = field(default_factory=utc_now)

    def __post_init__(self) -> None:
        if not self.component.strip():
            raise ValueError("component must not be empty")

        if self.reason is not None and not self.reason.strip():
            raise ValueError("reason must not be blank")

        if self.checked_at.tzinfo is None:
            raise ValueError("checked_at must be timezone-aware")
