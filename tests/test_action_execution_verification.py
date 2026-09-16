import pytest

from ayeon.contracts.action_attempt import ActionAttempt
from ayeon.contracts.action_execution import ActionExecution
from ayeon.contracts.action_execution_verification import ActionExecutionVerification
from ayeon.contracts.action_verification import ActionVerificationResult
from ayeon.contracts.actions import ActionIntent
from ayeon.contracts.authorization import (
    AuthorizationDecision,
    AuthorizationOutcome,
)
from ayeon.contracts.authorized_action import AuthorizedAction
from ayeon.contracts.common import (
    ResultState,
    TraceContext,
    new_action_id,
    new_attempt_id,
)
from ayeon.contracts.tool_execution import ToolExecutionResult
from ayeon.contracts.verification import VerificationState


def make_execution() -> ActionExecution:
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
        reason="Authorized for verification association test.",
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
        state=ResultState.SUCCESS,
        trace=attempt.trace,
        summary="Fake tool reported success.",
    )

    return ActionExecution(
        authorized_action=authorized,
        attempt=attempt,
        result=result,
    )


def test_action_execution_verification_accepts_matching_verification() -> None:
    execution = make_execution()

    verification = ActionVerificationResult(
        action_id=execution.attempt.action_id,
        attempt_id=execution.attempt.attempt_id,
        state=VerificationState.VERIFIED,
        verified_by="fake_verifier",
        trace=execution.attempt.trace,
        reason="Observed expected external effect.",
    )

    verified = ActionExecutionVerification(
        execution=execution,
        verification=verification,
    )

    assert verified.execution is execution
    assert verified.verification is verification

def test_action_execution_verification_rejects_wrong_action_id() -> None:
    execution = make_execution()

    verification = ActionVerificationResult(
        action_id=new_action_id(),
        attempt_id=execution.attempt.attempt_id,
        state=VerificationState.VERIFIED,
        verified_by="fake_verifier",
        trace=execution.attempt.trace,
        reason="Verification belongs to another action.",
    )

    with pytest.raises(ValueError, match="action_id"):
        ActionExecutionVerification(
            execution=execution,
            verification=verification,
        )

def test_action_execution_verification_rejects_wrong_attempt_id() -> None:
    execution = make_execution()

    verification = ActionVerificationResult(
        action_id=execution.attempt.action_id,
        attempt_id=new_attempt_id(),
        state=VerificationState.VERIFIED,
        verified_by="fake_verifier",
        trace=execution.attempt.trace,
        reason="Verification belongs to another attempt.",
    )

    with pytest.raises(ValueError, match="attempt_id"):
        ActionExecutionVerification(
            execution=execution,
            verification=verification,
        )

def test_action_execution_verification_rejects_wrong_correlation() -> None:
    execution = make_execution()
    unrelated_trace = TraceContext.root()

    verification = ActionVerificationResult(
        action_id=execution.attempt.action_id,
        attempt_id=execution.attempt.attempt_id,
        state=VerificationState.VERIFIED,
        verified_by="fake_verifier",
        trace=unrelated_trace,
        reason="Verification belongs to another correlation.",
    )

    with pytest.raises(ValueError, match="correlation"):
        ActionExecutionVerification(
            execution=execution,
            verification=verification,
        )