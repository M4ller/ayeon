import pytest

from ayeon.contracts.action_attempt import ActionAttempt
from ayeon.contracts.action_execution import ActionExecution
from ayeon.contracts.action_execution_verification import (
    ActionExecutionVerification,
)
from ayeon.contracts.action_outcome import ActionOutcome
from ayeon.contracts.action_verification import ActionVerificationResult
from ayeon.contracts.actions import (
    ActionIntent,
    ActionReversibility,
    ActionRisk,
)
from ayeon.contracts.authorization import (
    AuthorizationDecision,
    AuthorizationOutcome,
)
from ayeon.contracts.authorized_action import AuthorizedAction
from ayeon.contracts.common import (
    ActionId,
    AttemptId,
    CorrelationId,
    ResultState,
    TraceContext,
)
from ayeon.contracts.resolved_action_execution import ResolvedActionExecution
from ayeon.contracts.tool_execution import ToolExecutionResult
from ayeon.contracts.verification import VerificationState


def make_trace(value: str = "corr-1") -> TraceContext:
    return TraceContext(correlation_id=CorrelationId(value))


def make_verified_execution() -> ActionExecutionVerification:
    trace = make_trace()
    action_id = ActionId("action-1")
    attempt_id = AttemptId("attempt-1")

    intent = ActionIntent(
        action_type="test-tool",
        requested_by="test-suite",
        trace=trace,
        risk=ActionRisk.LOW,
        reversibility=ActionReversibility.REVERSIBLE,
        reason="Test action.",
        action_id=action_id,
    )

    decision = AuthorizationDecision(
        action_id=action_id,
        outcome=AuthorizationOutcome.ALLOW,
        decided_by="test-policy",
        trace=trace,
        reason="Allowed for test.",
    )

    authorized = AuthorizedAction(
        action=intent,
        authorization=decision,
    )

    attempt = ActionAttempt(
        action_id=action_id,
        attempt_id=attempt_id,
        tool_name="test-tool",
        trace=trace,
    )

    result = ToolExecutionResult(
        action_id=action_id,
        attempt_id=attempt_id,
        tool_name="test-tool",
        state=ResultState.SUCCESS,
        trace=trace,
        summary="Tool reported success.",
    )

    execution = ActionExecution(
        authorized_action=authorized,
        attempt=attempt,
        result=result,
    )

    verification = ActionVerificationResult(
        action_id=action_id,
        attempt_id=attempt_id,
        state=VerificationState.VERIFIED,
        verified_by="test-verifier",
        trace=trace,
        reason="Effect verified.",
    )

    return ActionExecutionVerification(
        execution=execution,
        verification=verification,
    )


def test_resolved_action_execution_accepts_consistent_outcome() -> None:
    verified_execution = make_verified_execution()

    outcome = ActionOutcome(
        action_id=ActionId("action-1"),
        attempt_id=AttemptId("attempt-1"),
        state=ResultState.SUCCESS,
        resolved_by="test-resolver",
        trace=make_trace(),
        reason="Execution and verification support success.",
    )

    resolved = ResolvedActionExecution(
        verified_execution=verified_execution,
        outcome=outcome,
    )

    assert resolved.outcome is outcome


def test_resolved_action_execution_rejects_wrong_action() -> None:
    verified_execution = make_verified_execution()

    outcome = ActionOutcome(
        action_id=ActionId("wrong-action"),
        attempt_id=AttemptId("attempt-1"),
        state=ResultState.UNKNOWN,
        resolved_by="test-resolver",
        trace=make_trace(),
        reason="Test mismatch.",
    )

    with pytest.raises(ValueError, match="outcome action_id"):
        ResolvedActionExecution(verified_execution, outcome)


def test_resolved_action_execution_rejects_wrong_attempt() -> None:
    verified_execution = make_verified_execution()

    outcome = ActionOutcome(
        action_id=ActionId("action-1"),
        attempt_id=AttemptId("wrong-attempt"),
        state=ResultState.UNKNOWN,
        resolved_by="test-resolver",
        trace=make_trace(),
        reason="Test mismatch.",
    )

    with pytest.raises(ValueError, match="outcome attempt_id"):
        ResolvedActionExecution(verified_execution, outcome)


def test_resolved_action_execution_rejects_wrong_correlation() -> None:
    verified_execution = make_verified_execution()

    outcome = ActionOutcome(
        action_id=ActionId("action-1"),
        attempt_id=AttemptId("attempt-1"),
        state=ResultState.UNKNOWN,
        resolved_by="test-resolver",
        trace=make_trace("wrong-correlation"),
        reason="Test mismatch.",
    )

    with pytest.raises(ValueError, match="outcome correlation"):
        ResolvedActionExecution(verified_execution, outcome)