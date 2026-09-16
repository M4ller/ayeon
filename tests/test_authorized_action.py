from dataclasses import FrozenInstanceError

import pytest

from ayeon.contracts.actions import ActionIntent
from ayeon.contracts.authorization import (
    AuthorizationDecision,
    AuthorizationOutcome,
)
from ayeon.contracts.authorized_action import AuthorizedAction
from ayeon.contracts.common import TraceContext


def make_action() -> ActionIntent:
    return ActionIntent(
        action_type="test.action",
        requested_by="cognition",
        trace=TraceContext.root(),
    )


def make_decision(
    action: ActionIntent,
    outcome: AuthorizationOutcome,
) -> AuthorizationDecision:
    return AuthorizationDecision(
        action_id=action.action_id,
        outcome=outcome,
        decided_by="authorization_policy",
        trace=action.trace,
        reason="Test authorization decision.",
    )


def test_allow_decision_creates_authorized_action() -> None:
    action = make_action()
    decision = make_decision(action, AuthorizationOutcome.ALLOW)

    authorized = AuthorizedAction(
        action=action,
        authorization=decision,
    )

    assert authorized.action is action
    assert authorized.authorization is decision


def test_require_approval_cannot_create_authorized_action() -> None:
    action = make_action()
    decision = make_decision(
        action,
        AuthorizationOutcome.REQUIRE_APPROVAL,
    )

    with pytest.raises(ValueError, match="ALLOW"):
        AuthorizedAction(
            action=action,
            authorization=decision,
        )


def test_deny_cannot_create_authorized_action() -> None:
    action = make_action()
    decision = make_decision(action, AuthorizationOutcome.DENY)

    with pytest.raises(ValueError, match="ALLOW"):
        AuthorizedAction(
            action=action,
            authorization=decision,
        )


def test_authorization_must_match_action_id() -> None:
    action = make_action()
    other_action = make_action()
    decision = make_decision(other_action, AuthorizationOutcome.ALLOW)

    with pytest.raises(ValueError, match="action_id"):
        AuthorizedAction(
            action=action,
            authorization=decision,
        )


def test_authorization_must_match_correlation() -> None:
    action = make_action()

    decision = AuthorizationDecision(
        action_id=action.action_id,
        outcome=AuthorizationOutcome.ALLOW,
        decided_by="authorization_policy",
        trace=TraceContext.root(),
        reason="Wrong trace.",
    )

    with pytest.raises(ValueError, match="correlation"):
        AuthorizedAction(
            action=action,
            authorization=decision,
        )


def test_authorized_action_is_immutable() -> None:
    action = make_action()
    decision = make_decision(action, AuthorizationOutcome.ALLOW)

    authorized = AuthorizedAction(
        action=action,
        authorization=decision,
    )

    with pytest.raises(FrozenInstanceError):
        authorized.action = make_action()


def test_authorized_action_has_no_execution_methods() -> None:
    action = make_action()
    decision = make_decision(action, AuthorizationOutcome.ALLOW)

    authorized = AuthorizedAction(
        action=action,
        authorization=decision,
    )

    assert not hasattr(authorized, "execute")
    assert not hasattr(authorized, "run")