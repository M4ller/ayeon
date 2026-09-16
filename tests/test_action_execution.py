import pytest

from ayeon.contracts.action_attempt import ActionAttempt
from ayeon.contracts.action_execution import ActionExecution
from ayeon.contracts.actions import ActionIntent
from ayeon.contracts.authorization import (
    AuthorizationDecision,
    AuthorizationOutcome,
)
from ayeon.contracts.authorized_action import AuthorizedAction
from ayeon.contracts.common import ResultState, TraceContext
from ayeon.contracts.tool_execution import ToolExecutionResult


def make_authorized_action() -> AuthorizedAction:
    action = ActionIntent(
        action_type="test.action",
        requested_by="cognition",
        trace=TraceContext.root(),
    )

    decision = AuthorizationDecision(
        action_id=action.action_id,
        outcome=AuthorizationOutcome.ALLOW,
        decided_by="authorization_policy",
        trace=action.trace,
        reason="Authorized for test.",
    )

    return AuthorizedAction(
        action=action,
        authorization=decision,
    )


def make_attempt(
    authorized: AuthorizedAction,
) -> ActionAttempt:
    return ActionAttempt(
        action_id=authorized.action.action_id,
        tool_name="test_tool",
        trace=authorized.action.trace,
    )


def make_result(
    attempt: ActionAttempt,
) -> ToolExecutionResult:
    return ToolExecutionResult(
        action_id=attempt.action_id,
        attempt_id=attempt.attempt_id,
        tool_name=attempt.tool_name,
        state=ResultState.SUCCESS,
        trace=attempt.trace,
        summary="Tool reported success.",
    )


def test_action_execution_accepts_matching_chain() -> None:
    authorized = make_authorized_action()
    attempt = make_attempt(authorized)
    result = make_result(attempt)

    execution = ActionExecution(
        authorized_action=authorized,
        attempt=attempt,
        result=result,
    )

    assert execution.authorized_action is authorized
    assert execution.attempt is attempt
    assert execution.result is result


def test_action_execution_rejects_attempt_for_wrong_action() -> None:
    authorized = make_authorized_action()
    other = make_authorized_action()
    attempt = make_attempt(other)
    result = make_result(attempt)

    with pytest.raises(ValueError, match="action_id"):
        ActionExecution(
            authorized_action=authorized,
            attempt=attempt,
            result=result,
        )


def test_action_execution_rejects_result_for_wrong_action() -> None:
    authorized = make_authorized_action()
    attempt = make_attempt(authorized)
    other = make_authorized_action()
    other_attempt = make_attempt(other)
    result = make_result(other_attempt)

    with pytest.raises(ValueError, match="action_id"):
        ActionExecution(
            authorized_action=authorized,
            attempt=attempt,
            result=result,
        )


def test_action_execution_rejects_result_for_wrong_attempt() -> None:
    authorized = make_authorized_action()
    attempt = make_attempt(authorized)
    other_attempt = make_attempt(authorized)
    result = make_result(other_attempt)

    with pytest.raises(ValueError, match="attempt_id"):
        ActionExecution(
            authorized_action=authorized,
            attempt=attempt,
            result=result,
        )


def test_action_execution_rejects_wrong_attempt_correlation() -> None:
    authorized = make_authorized_action()

    attempt = ActionAttempt(
        action_id=authorized.action.action_id,
        tool_name="test_tool",
        trace=TraceContext.root(),
    )
    result = make_result(attempt)

    with pytest.raises(ValueError, match="correlation"):
        ActionExecution(
            authorized_action=authorized,
            attempt=attempt,
            result=result,
        )


def test_action_execution_rejects_wrong_result_correlation() -> None:
    authorized = make_authorized_action()
    attempt = make_attempt(authorized)

    result = ToolExecutionResult(
        action_id=attempt.action_id,
        attempt_id=attempt.attempt_id,
        tool_name=attempt.tool_name,
        state=ResultState.SUCCESS,
        trace=TraceContext.root(),
        summary="Wrong result correlation.",
    )

    with pytest.raises(ValueError, match="correlation"):
        ActionExecution(
            authorized_action=authorized,
            attempt=attempt,
            result=result,
        )

def test_action_execution_rejects_wrong_tool_name() -> None:
    authorized = make_authorized_action()
    attempt = make_attempt(authorized)

    result = ToolExecutionResult(
        action_id=attempt.action_id,
        attempt_id=attempt.attempt_id,
        tool_name="other_tool",
        state=ResultState.SUCCESS,
        trace=attempt.trace,
        summary="Result from wrong tool.",
    )

    with pytest.raises(ValueError, match="tool_name"):
        ActionExecution(
            authorized_action=authorized,
            attempt=attempt,
            result=result,
        )