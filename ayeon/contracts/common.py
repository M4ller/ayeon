"""Common typed primitives used across Ayeon Core."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from enum import StrEnum
from typing import NewType
from uuid import UUID, uuid4

EventId = NewType("EventId", UUID)
CorrelationId = NewType("CorrelationId", UUID)
CausationId = NewType("CausationId", UUID)
RequestId = NewType("RequestId", UUID)
TaskId = NewType("TaskId", UUID)
ActionId = NewType("ActionId", UUID)
AttemptId = NewType("AttemptId", UUID)
SessionId = NewType("SessionId", UUID)
MemoryIntentId = NewType("MemoryIntentId", UUID)


def utc_now() -> datetime:
    """Return the current timezone-aware UTC datetime."""
    return datetime.now(UTC)


def new_event_id() -> EventId:
    return EventId(uuid4())


def new_correlation_id() -> CorrelationId:
    return CorrelationId(uuid4())


def new_request_id() -> RequestId:
    return RequestId(uuid4())


def new_task_id() -> TaskId:
    return TaskId(uuid4())


def new_action_id() -> ActionId:
    return ActionId(uuid4())


def new_attempt_id() -> AttemptId:
    return AttemptId(uuid4())


def new_session_id() -> SessionId:
    return SessionId(uuid4())


def new_memory_intent_id() -> MemoryIntentId:
    return MemoryIntentId(uuid4())


class ResultState(StrEnum):
    """Canonical outcome state for operations."""

    SUCCESS = "success"
    FAILED = "failed"
    UNKNOWN = "unknown"


class HealthState(StrEnum):
    """Runtime health state of an Ayeon module."""

    HEALTHY = "healthy"
    DEGRADED = "degraded"
    FAILED = "failed"
    UNAVAILABLE = "unavailable"
    RECOVERING = "recovering"


@dataclass(frozen=True, slots=True)
class TraceContext:
    """Trace identifiers used to correlate operations without storing payloads."""

    correlation_id: CorrelationId
    causation_id: CausationId | None = None

    @classmethod
    def root(cls) -> TraceContext:
        """Create a new root trace."""
        return cls(correlation_id=new_correlation_id())

    def caused_by(self, event_id: EventId) -> TraceContext:
        """Create a child trace linked to a direct causal event."""
        return TraceContext(
            correlation_id=self.correlation_id,
            causation_id=CausationId(event_id),
        )
