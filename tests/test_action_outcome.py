from datetime import datetime, timezone

import pytest

from ayeon.contracts.action_outcome import ActionOutcome
from ayeon.contracts.common import (
    ActionId,
    AttemptId,
    CorrelationId,
    ResultState,
    TraceContext,
)


def make_trace() -> TraceContext:
    return TraceContext(
        correlation_id=CorrelationId("corr-1"),
    )


def test_action_outcome_accepts_valid_final_state() -> None:
    outcome = ActionOutcome(
        action_id=ActionId("action-1"),
        attempt_id=AttemptId("attempt-1"),
        state=ResultState.SUCCESS,
        resolved_by="deterministic-outcome-resolver",
        trace=make_trace(),
        reason="Execution succeeded and external effect was verified.",
        resolved_at=datetime.now(timezone.utc),
    )

    assert outcome.state is ResultState.SUCCESS
    assert outcome.resolved_by == "deterministic-outcome-resolver"


def test_action_outcome_rejects_blank_resolved_by() -> None:
    with pytest.raises(ValueError, match="resolved_by must not be empty"):
        ActionOutcome(
            action_id=ActionId("action-1"),
            attempt_id=AttemptId("attempt-1"),
            state=ResultState.UNKNOWN,
            resolved_by=" ",
            trace=make_trace(),
            reason="Effect could not be verified.",
        )


def test_action_outcome_rejects_blank_reason() -> None:
    with pytest.raises(ValueError, match="reason must not be empty"):
        ActionOutcome(
            action_id=ActionId("action-1"),
            attempt_id=AttemptId("attempt-1"),
            state=ResultState.FAILED,
            resolved_by="deterministic-outcome-resolver",
            trace=make_trace(),
            reason=" ",
        )


def test_action_outcome_rejects_naive_resolved_at() -> None:
    with pytest.raises(ValueError, match="resolved_at must be timezone-aware"):
        ActionOutcome(
            action_id=ActionId("action-1"),
            attempt_id=AttemptId("attempt-1"),
            state=ResultState.SUCCESS,
            resolved_by="deterministic-outcome-resolver",
            trace=make_trace(),
            reason="Effect verified.",
            resolved_at=datetime(2026, 1, 1),
        )