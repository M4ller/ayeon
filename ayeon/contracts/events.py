"""Event contracts for communication across Ayeon Core."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field
from datetime import datetime
from enum import StrEnum

from ayeon.contracts.common import (
    EventId,
    TraceContext,
    new_event_id,
    utc_now,
)


class EventPersistence(StrEnum):
    """Persistence policy for an event."""

    EPHEMERAL = "ephemeral"
    AUDIT = "audit"
    HISTORICAL = "historical"


@dataclass(frozen=True, slots=True)
class AyeonEvent:
    """Immutable event exchanged between Ayeon modules."""

    event_type: str
    source: str
    trace: TraceContext
    persistence: EventPersistence = EventPersistence.EPHEMERAL
    payload: Mapping[str, object] = field(default_factory=dict)
    event_id: EventId = field(default_factory=new_event_id)
    occurred_at: datetime = field(default_factory=utc_now)

    def __post_init__(self) -> None:
        if not self.event_type.strip():
            raise ValueError("event_type must not be empty")

        if not self.source.strip():
            raise ValueError("source must not be empty")

        if self.occurred_at.tzinfo is None:
            raise ValueError("occurred_at must be timezone-aware")
