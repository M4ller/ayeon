from ayeon.contracts.actions import (
    ActionIntent,
    ActionReversibility,
    ActionRisk,
)
from ayeon.contracts.authorization import (
    AuthorizationOutcome,
    AuthorizationRequest,
)
from ayeon.contracts.common import TraceContext
from ayeon.security.authorization.policy import AuthorizationPolicy


def make_request(
    *,
    risk: ActionRisk = ActionRisk.LOW,
) -> AuthorizationRequest:
    trace = TraceContext.root()

    action = ActionIntent(
        action_type="test.action",
        requested_by="cognition",
        trace=trace,
        parameters={"value": 42},
        risk=risk,
        reversibility=ActionReversibility.REVERSIBLE,
        reason="Test authorization policy.",
    )

    return AuthorizationRequest(
        action=action,
        trace=trace,
    )


def test_policy_requires_approval_by_default() -> None:
    policy = AuthorizationPolicy()
    request = make_request()

    decision = policy.evaluate(request)

    assert decision.action_id == request.action.action_id
    assert decision.outcome is AuthorizationOutcome.REQUIRE_APPROVAL
    assert decision.decided_by == "authorization_policy"


def test_policy_preserves_trace() -> None:
    policy = AuthorizationPolicy()
    request = make_request()

    decision = policy.evaluate(request)

    assert decision.trace == request.trace


def test_high_risk_action_is_not_automatically_allowed() -> None:
    policy = AuthorizationPolicy()
    request = make_request(risk=ActionRisk.HIGH)

    decision = policy.evaluate(request)

    assert decision.outcome is not AuthorizationOutcome.ALLOW


def test_critical_risk_action_is_not_automatically_allowed() -> None:
    policy = AuthorizationPolicy()
    request = make_request(risk=ActionRisk.CRITICAL)

    decision = policy.evaluate(request)

    assert decision.outcome is not AuthorizationOutcome.ALLOW

def test_matching_approval_allows_action() -> None:
    from ayeon.contracts.approval import ApprovalEvidence

    policy = AuthorizationPolicy(approval_authorities={"felipe"})
    request = make_request()

    approval = ApprovalEvidence(
        action_id=request.action.action_id,
        approved_by="felipe",
        trace=request.trace,
        reason="Explicitly approved.",
    )

    decision = policy.evaluate(request, approval=approval)

    assert decision.outcome is AuthorizationOutcome.ALLOW
    assert decision.action_id == request.action.action_id


def test_approval_for_different_action_does_not_allow() -> None:
    from ayeon.contracts.approval import ApprovalEvidence
    from ayeon.contracts.common import new_action_id

    policy = AuthorizationPolicy()
    request = make_request()

    approval = ApprovalEvidence(
        action_id=new_action_id(),
        approved_by="felipe",
        trace=request.trace,
        reason="Approved another action.",
    )

    decision = policy.evaluate(request, approval=approval)

    assert decision.outcome is not AuthorizationOutcome.ALLOW


def test_approval_with_different_correlation_does_not_allow() -> None:
    from ayeon.contracts.approval import ApprovalEvidence

    policy = AuthorizationPolicy()
    request = make_request()

    approval = ApprovalEvidence(
        action_id=request.action.action_id,
        approved_by="felipe",
        trace=TraceContext.root(),
        reason="Approval from another trace.",
    )

    decision = policy.evaluate(request, approval=approval)

    assert decision.outcome is not AuthorizationOutcome.ALLOW

def test_configured_authority_can_approve_action() -> None:
    from ayeon.contracts.approval import ApprovalEvidence

    policy = AuthorizationPolicy(approval_authorities={"felipe"})
    request = make_request()

    approval = ApprovalEvidence(
        action_id=request.action.action_id,
        approved_by="felipe",
        trace=request.trace,
        reason="Explicitly approved.",
    )

    decision = policy.evaluate(request, approval=approval)

    assert decision.outcome is AuthorizationOutcome.ALLOW


def test_unknown_authority_cannot_approve_action() -> None:
    from ayeon.contracts.approval import ApprovalEvidence

    policy = AuthorizationPolicy(approval_authorities={"felipe"})
    request = make_request()

    approval = ApprovalEvidence(
        action_id=request.action.action_id,
        approved_by="unknown_actor",
        trace=request.trace,
        reason="Attempted approval.",
    )

    decision = policy.evaluate(request, approval=approval)

    assert decision.outcome is not AuthorizationOutcome.ALLOW