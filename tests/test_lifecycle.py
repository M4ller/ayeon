from datetime import datetime

import pytest

from ayeon.contracts.common import TraceContext
from ayeon.contracts.lifecycle import LifecycleState, LifecycleTransition


def test_lifecycle_transition_records_state_change() -> None:
    trace = TraceContext.root()

    transition = LifecycleTransition(
        previous=LifecycleState.STOPPED,
        target=LifecycleState.BOOTING,
        reason="Runtime startup requested.",
        initiated_by="runtime",
        trace=trace,
    )

    assert transition.previous is LifecycleState.STOPPED
    assert transition.target is LifecycleState.BOOTING
    assert transition.trace.correlation_id == trace.correlation_id


def test_same_state_transition_is_rejected() -> None:
    with pytest.raises(
        ValueError,
        match="lifecycle transition must change state",
    ):
        LifecycleTransition(
            previous=LifecycleState.RUNNING,
            target=LifecycleState.RUNNING,
            reason="No state change.",
            initiated_by="runtime",
            trace=TraceContext.root(),
        )


def test_empty_reason_is_rejected() -> None:
    with pytest.raises(ValueError, match="reason must not be empty"):
        LifecycleTransition(
            previous=LifecycleState.BOOTING,
            target=LifecycleState.VERIFYING,
            reason=" ",
            initiated_by="runtime",
            trace=TraceContext.root(),
        )


def test_empty_initiator_is_rejected() -> None:
    with pytest.raises(ValueError, match="initiated_by must not be empty"):
        LifecycleTransition(
            previous=LifecycleState.BOOTING,
            target=LifecycleState.VERIFYING,
            reason="Begin identity verification.",
            initiated_by=" ",
            trace=TraceContext.root(),
        )


def test_transition_timestamp_is_timezone_aware() -> None:
    transition = LifecycleTransition(
        previous=LifecycleState.BOOTING,
        target=LifecycleState.VERIFYING,
        reason="Begin verification.",
        initiated_by="runtime",
        trace=TraceContext.root(),
    )

    assert transition.occurred_at.tzinfo is not None


def test_naive_transition_timestamp_is_rejected() -> None:
    with pytest.raises(ValueError, match="occurred_at must be timezone-aware"):
        LifecycleTransition(
            previous=LifecycleState.BOOTING,
            target=LifecycleState.VERIFYING,
            reason="Begin verification.",
            initiated_by="runtime",
            trace=TraceContext.root(),
            occurred_at=datetime(2026, 1, 1),
        )
