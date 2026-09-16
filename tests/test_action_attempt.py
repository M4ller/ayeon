from dataclasses import FrozenInstanceError
from datetime import datetime

import pytest

from ayeon.contracts.action_attempt import ActionAttempt
from ayeon.contracts.common import TraceContext, new_action_id


def make_attempt() -> ActionAttempt:
    return ActionAttempt(
        action_id=new_action_id(),
        tool_name="test_tool",
        trace=TraceContext.root(),
    )


def test_action_attempt_has_unique_identity() -> None:
    first = make_attempt()
    second = make_attempt()

    assert first.attempt_id != second.attempt_id


def test_action_attempt_preserves_action_id() -> None:
    action_id = new_action_id()

    attempt = ActionAttempt(
        action_id=action_id,
        tool_name="test_tool",
        trace=TraceContext.root(),
    )

    assert attempt.action_id == action_id


def test_action_attempt_preserves_tool_name_and_trace() -> None:
    trace = TraceContext.root()

    attempt = ActionAttempt(
        action_id=new_action_id(),
        tool_name="test_tool",
        trace=trace,
    )

    assert attempt.tool_name == "test_tool"
    assert attempt.trace == trace


def test_action_attempt_has_timezone_aware_started_at() -> None:
    attempt = make_attempt()

    assert isinstance(attempt.started_at, datetime)
    assert attempt.started_at.tzinfo is not None


def test_action_attempt_rejects_blank_tool_name() -> None:
    with pytest.raises(ValueError, match="tool_name"):
        ActionAttempt(
            action_id=new_action_id(),
            tool_name=" ",
            trace=TraceContext.root(),
        )


def test_action_attempt_is_immutable() -> None:
    attempt = make_attempt()

    with pytest.raises(FrozenInstanceError):
        attempt.tool_name = "other_tool"


def test_action_attempt_does_not_claim_result_state() -> None:
    attempt = make_attempt()

    assert not hasattr(attempt, "state")
    assert not hasattr(attempt, "success")
    assert not hasattr(attempt, "verified")