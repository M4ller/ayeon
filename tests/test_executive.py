from ayeon.contracts.actions import (
    ActionIntent,
    ActionReversibility,
    ActionRisk,
)
from ayeon.contracts.authorization import AuthorizationRequest
from ayeon.contracts.common import TraceContext
from ayeon.runtime.executive import Executive


def make_action() -> ActionIntent:
    trace = TraceContext.root()

    return ActionIntent(
        action_type="test.action",
        requested_by="cognition",
        trace=trace,
        parameters={"value": 42},
        risk=ActionRisk.LOW,
        reversibility=ActionReversibility.REVERSIBLE,
        reason="Test executive boundary.",
    )


def test_executive_creates_authorization_request() -> None:
    executive = Executive()
    action = make_action()

    request = executive.request_authorization(action)

    assert isinstance(request, AuthorizationRequest)
    assert request.action is action
    assert request.trace.correlation_id == action.trace.correlation_id


def test_executive_does_not_expose_execution_methods() -> None:
    executive = Executive()

    assert not hasattr(executive, "execute")
    assert not hasattr(executive, "run")
    assert not hasattr(executive, "execute_tool")


def test_executive_does_not_expose_authorization_decision_methods() -> None:
    executive = Executive()

    assert not hasattr(executive, "authorize")
    assert not hasattr(executive, "allow")
    assert not hasattr(executive, "approve")

def test_authorization_request_preserves_action_identity() -> None:
    executive = Executive()
    action = make_action()

    request = executive.request_authorization(action)

    assert request.action.action_id == action.action_id
    assert request.action is action


def test_authorization_request_preserves_trace() -> None:
    executive = Executive()
    action = make_action()

    request = executive.request_authorization(action)

    assert request.trace == action.trace
    assert request.trace.correlation_id == action.trace.correlation_id

def test_executive_materializes_allowed_action() -> None:
    from ayeon.contracts.authorization import (
        AuthorizationDecision,
        AuthorizationOutcome,
    )
    from ayeon.contracts.authorized_action import AuthorizedAction

    executive = Executive()
    action = make_action()

    decision = AuthorizationDecision(
        action_id=action.action_id,
        outcome=AuthorizationOutcome.ALLOW,
        decided_by="authorization_policy",
        trace=action.trace,
        reason="Authorized for execution eligibility.",
    )

    authorized = executive.materialize_authorized_action(
        action=action,
        decision=decision,
    )

    assert isinstance(authorized, AuthorizedAction)
    assert authorized.action is action
    assert authorized.authorization is decision


def test_executive_rejects_require_approval_decision() -> None:
    from ayeon.contracts.authorization import (
        AuthorizationDecision,
        AuthorizationOutcome,
    )

    executive = Executive()
    action = make_action()

    decision = AuthorizationDecision(
        action_id=action.action_id,
        outcome=AuthorizationOutcome.REQUIRE_APPROVAL,
        decided_by="authorization_policy",
        trace=action.trace,
        reason="Approval still required.",
    )

    try:
        executive.materialize_authorized_action(
            action=action,
            decision=decision,
        )
    except ValueError as exc:
        assert "ALLOW" in str(exc)
    else:
        raise AssertionError("REQUIRE_APPROVAL must not become AuthorizedAction")


def test_executive_rejects_deny_decision() -> None:
    from ayeon.contracts.authorization import (
        AuthorizationDecision,
        AuthorizationOutcome,
    )

    executive = Executive()
    action = make_action()

    decision = AuthorizationDecision(
        action_id=action.action_id,
        outcome=AuthorizationOutcome.DENY,
        decided_by="authorization_policy",
        trace=action.trace,
        reason="Action denied.",
    )

    try:
        executive.materialize_authorized_action(
            action=action,
            decision=decision,
        )
    except ValueError as exc:
        assert "ALLOW" in str(exc)
    else:
        raise AssertionError("DENY must not become AuthorizedAction")