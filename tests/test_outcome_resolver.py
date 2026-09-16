import pytest

from ayeon.contracts.action_attempt import ActionAttempt
from ayeon.contracts.action_execution import ActionExecution
from ayeon.contracts.action_execution_verification import (
    ActionExecutionVerification,
)
from ayeon.contracts.action_verification import ActionVerificationResult
from ayeon.contracts.actions import ActionIntent
from ayeon.contracts.authorization import (
    AuthorizationDecision,
    AuthorizationOutcome,
)
from ayeon.contracts.authorized_action import AuthorizedAction
from ayeon.contracts.common import ResultState, TraceContext
from ayeon.contracts.resolved_action_execution import ResolvedActionExecution
from ayeon.contracts.tool_execution import ToolExecutionResult
from ayeon.contracts.verification import VerificationState
from ayeon.runtime.outcome_resolver import OutcomeResolver


def make_verified_execution(
    tool_state: ResultState,
    verification_state: VerificationState,
) -> ActionExecutionVerification:
    action = ActionIntent(
        action_type="fake_tool",
        requested_by="cognition",
        trace=TraceContext.root(),
    )

    decision = AuthorizationDecision(
        action_id=action.action_id,
        outcome=AuthorizationOutcome.ALLOW,
        decided_by="authorization_policy",
        trace=action.trace,
        reason="Authorized for outcome resolver test.",
    )

    authorized = AuthorizedAction(
        action=action,
        authorization=decision,
    )

    attempt = ActionAttempt(
        action_id=action.action_id,
        tool_name="fake_tool",
        trace=action.trace,
    )

    result = ToolExecutionResult(
        action_id=action.action_id,
        attempt_id=attempt.attempt_id,
        tool_name=attempt.tool_name,
        state=tool_state,
        trace=attempt.trace,
        summary="Tool execution fixture.",
    )

    execution = ActionExecution(
        authorized_action=authorized,
        attempt=attempt,
        result=result,
    )

    verification = ActionVerificationResult(
        action_id=action.action_id,
        attempt_id=attempt.attempt_id,
        state=verification_state,
        verified_by="fake_tool",
        trace=attempt.trace,
        reason="Verification fixture.",
    )

    return ActionExecutionVerification(
        execution=execution,
        verification=verification,
    )


@pytest.mark.parametrize(
    ("tool_state", "verification_state", "expected"),
    [
        (
            ResultState.SUCCESS,
            VerificationState.VERIFIED,
            ResultState.SUCCESS,
        ),
        (
            ResultState.SUCCESS,
            VerificationState.FAILED,
            ResultState.FAILED,
        ),
        (
            ResultState.SUCCESS,
            VerificationState.UNKNOWN,
            ResultState.UNKNOWN,
        ),
        (
            ResultState.FAILED,
            VerificationState.VERIFIED,
            ResultState.FAILED,
        ),
        (
            ResultState.FAILED,
            VerificationState.FAILED,
            ResultState.FAILED,
        ),
        (
            ResultState.FAILED,
            VerificationState.UNKNOWN,
            ResultState.FAILED,
        ),
        (
            ResultState.UNKNOWN,
            VerificationState.VERIFIED,
            ResultState.UNKNOWN,
        ),
        (
            ResultState.UNKNOWN,
            VerificationState.FAILED,
            ResultState.UNKNOWN,
        ),
        (
            ResultState.UNKNOWN,
            VerificationState.UNKNOWN,
            ResultState.UNKNOWN,
        ),
    ],
)
def test_outcome_resolver_uses_conservative_state_matrix(
    tool_state: ResultState,
    verification_state: VerificationState,
    expected: ResultState,
) -> None:
    evidence = make_verified_execution(
        tool_state,
        verification_state,
    )

    resolved = OutcomeResolver().resolve(evidence)

    assert isinstance(resolved, ResolvedActionExecution)
    assert resolved.verified_execution is evidence
    assert resolved.outcome.state is expected
    assert (
        resolved.outcome.action_id
        == evidence.execution.attempt.action_id
    )
    assert (
        resolved.outcome.attempt_id
        == evidence.execution.attempt.attempt_id
    )
    assert (
        resolved.outcome.trace.correlation_id
        == evidence.execution.attempt.trace.correlation_id
    )


def test_outcome_resolver_identifies_itself() -> None:
    evidence = make_verified_execution(
        ResultState.SUCCESS,
        VerificationState.VERIFIED,
    )

    resolved = OutcomeResolver().resolve(evidence)

    assert resolved.outcome.resolved_by == "outcome_resolver"
    assert resolved.outcome.reason.strip()