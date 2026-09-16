from datetime import datetime

import pytest

from ayeon.contracts.common import TraceContext
from ayeon.contracts.events import AyeonEvent, EventPersistence


def test_event_has_identity_time_and_trace() -> None:
    trace = TraceContext.root()

    event = AyeonEvent(
        event_type="runtime.started",
        source="runtime",
        trace=trace,
    )

    assert event.event_id is not None
    assert event.occurred_at.tzinfo is not None
    assert event.trace.correlation_id == trace.correlation_id


def test_event_defaults_to_ephemeral() -> None:
    event = AyeonEvent(
        event_type="attention.changed",
        source="attention",
        trace=TraceContext.root(),
    )

    assert event.persistence is EventPersistence.EPHEMERAL


def test_event_can_be_historical_without_becoming_memory() -> None:
    event = AyeonEvent(
        event_type="identity.checkpoint.created",
        source="identity",
        trace=TraceContext.root(),
        persistence=EventPersistence.HISTORICAL,
    )

    assert event.persistence is EventPersistence.HISTORICAL
    assert "memory" not in event.event_type


def test_empty_event_type_is_rejected() -> None:
    with pytest.raises(ValueError, match="event_type must not be empty"):
        AyeonEvent(
            event_type=" ",
            source="runtime",
            trace=TraceContext.root(),
        )


def test_naive_event_timestamp_is_rejected() -> None:
    with pytest.raises(ValueError, match="occurred_at must be timezone-aware"):
        AyeonEvent(
            event_type="runtime.started",
            source="runtime",
            trace=TraceContext.root(),
            occurred_at=datetime(2026, 1, 1),
        )
