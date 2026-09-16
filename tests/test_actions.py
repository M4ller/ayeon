from datetime import datetime

import pytest

from ayeon.contracts.actions import (
    ActionIntent,
    ActionReversibility,
    ActionRisk,
)
from ayeon.contracts.common import TraceContext


def test_action_intent_has_identity_and_trace() -> None:
    trace = TraceContext.root()

    intent = ActionIntent(
        action_type="file.read",
        requested_by="cognition",
        trace=trace,
    )

    assert intent.action_id is not None
    assert intent.trace.correlation_id == trace.correlation_id
    assert intent.created_at.tzinfo is not None


def test_action_intent_contains_no_authorization_state() -> None:
    intent = ActionIntent(
        action_type="file.write",
        requested_by="cognition",
        trace=TraceContext.root(),
    )

    assert not hasattr(intent, "authorized")
    assert not hasattr(intent, "authorization")
    assert not hasattr(intent, "permission")


def test_action_intent_has_no_execution_capability() -> None:
    intent = ActionIntent(
        action_type="tool.execute",
        requested_by="cognition",
        trace=TraceContext.root(),
    )

    assert not hasattr(intent, "execute")
    assert not hasattr(intent, "run")


def test_high_risk_irreversible_action_is_only_a_proposal() -> None:
    intent = ActionIntent(
        action_type="file.delete",
        requested_by="cognition",
        trace=TraceContext.root(),
        risk=ActionRisk.HIGH,
        reversibility=ActionReversibility.IRREVERSIBLE,
        reason="Obsolete file detected",
    )

    assert intent.risk is ActionRisk.HIGH
    assert intent.reversibility is ActionReversibility.IRREVERSIBLE
    assert not hasattr(intent, "authorized")


def test_empty_action_type_is_rejected() -> None:
    with pytest.raises(ValueError, match="action_type must not be empty"):
        ActionIntent(
            action_type=" ",
            requested_by="cognition",
            trace=TraceContext.root(),
        )


def test_naive_created_at_is_rejected() -> None:
    with pytest.raises(ValueError, match="created_at must be timezone-aware"):
        ActionIntent(
            action_type="file.read",
            requested_by="cognition",
            trace=TraceContext.root(),
            created_at=datetime(2026, 1, 1),
        )
