from datetime import datetime

import pytest

from ayeon.contracts.actions import ActionIntent
from ayeon.contracts.authorization import (
    AuthorizationDecision,
    AuthorizationOutcome,
    AuthorizationRequest,
)
from ayeon.contracts.common import TraceContext


def test_authorization_request_tracks_exact_action() -> None:
    trace = TraceContext.root()
    action = ActionIntent(
        action_type="file.write",
        requested_by="cognition",
        trace=trace,
    )

    request = AuthorizationRequest(
        action=action,
        trace=trace,
    )

    assert request.action.action_id == action.action_id


def test_authorization_request_rejects_unrelated_trace() -> None:
    action = ActionIntent(
        action_type="file.write",
        requested_by="cognition",
        trace=TraceContext.root(),
    )

    with pytest.raises(
        ValueError,
        match="action must share AuthorizationRequest correlation_id",
    ):
        AuthorizationRequest(
            action=action,
            trace=TraceContext.root(),
        )


def test_authorization_can_require_explicit_approval() -> None:
    trace = TraceContext.root()
    action = ActionIntent(
        action_type="email.send",
        requested_by="cognition",
        trace=trace,
    )

    decision = AuthorizationDecision(
        action_id=action.action_id,
        outcome=AuthorizationOutcome.REQUIRE_APPROVAL,
        decided_by="authorization_policy",
        trace=trace,
        reason="External communication requires explicit approval.",
    )

    assert decision.outcome is AuthorizationOutcome.REQUIRE_APPROVAL


def test_cognition_cannot_grant_authorization() -> None:
    trace = TraceContext.root()
    action = ActionIntent(
        action_type="file.delete",
        requested_by="cognition",
        trace=trace,
    )

    with pytest.raises(ValueError, match="cognition cannot grant authorization"):
        AuthorizationDecision(
            action_id=action.action_id,
            outcome=AuthorizationOutcome.ALLOW,
            decided_by="cognition",
            trace=trace,
            reason="I decided to allow myself.",
        )


def test_empty_decision_reason_is_rejected() -> None:
    trace = TraceContext.root()
    action = ActionIntent(
        action_type="file.read",
        requested_by="cognition",
        trace=trace,
    )

    with pytest.raises(ValueError, match="reason must not be empty"):
        AuthorizationDecision(
            action_id=action.action_id,
            outcome=AuthorizationOutcome.ALLOW,
            decided_by="authorization_policy",
            trace=trace,
            reason=" ",
        )


def test_naive_decision_timestamp_is_rejected() -> None:
    trace = TraceContext.root()
    action = ActionIntent(
        action_type="file.read",
        requested_by="cognition",
        trace=trace,
    )

    with pytest.raises(ValueError, match="decided_at must be timezone-aware"):
        AuthorizationDecision(
            action_id=action.action_id,
            outcome=AuthorizationOutcome.ALLOW,
            decided_by="authorization_policy",
            trace=trace,
            reason="Policy allows read access.",
            decided_at=datetime(2026, 1, 1),
        )
