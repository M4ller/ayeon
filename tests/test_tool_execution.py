from dataclasses import FrozenInstanceError

import pytest

from ayeon.contracts.common import ResultState, TraceContext, new_action_id, new_attempt_id
from ayeon.contracts.tool_execution import ToolExecutionResult


def make_result(
    state: ResultState = ResultState.SUCCESS,
) -> ToolExecutionResult:
    return ToolExecutionResult(
        action_id=new_action_id(),
        attempt_id=new_attempt_id(),
        tool_name="test_tool",
        state=state,
        trace=TraceContext.root(),
        summary="Tool execution result.",
    )


def test_tool_execution_result_preserves_state() -> None:
    result = make_result(ResultState.SUCCESS)

    assert result.tool_name == "test_tool"
    assert result.state is ResultState.SUCCESS


def test_tool_execution_result_supports_failed() -> None:
    result = make_result(ResultState.FAILED)

    assert result.state is ResultState.FAILED


def test_tool_execution_result_supports_unknown() -> None:
    result = make_result(ResultState.UNKNOWN)

    assert result.state is ResultState.UNKNOWN


def test_tool_execution_result_is_immutable() -> None:
    result = make_result()

    with pytest.raises(FrozenInstanceError):
        result.state = ResultState.FAILED


def test_tool_execution_result_rejects_blank_tool_name() -> None:
    with pytest.raises(ValueError, match="tool_name"):
        ToolExecutionResult(
            action_id=new_action_id(),
            attempt_id=new_attempt_id(),
            tool_name=" ",
            state=ResultState.SUCCESS,
            trace=TraceContext.root(),
            summary="Result.",
        )


def test_tool_execution_result_rejects_blank_summary() -> None:
    with pytest.raises(ValueError, match="summary"):
        ToolExecutionResult(
            action_id=new_action_id(),
            attempt_id=new_attempt_id(),
            tool_name="test_tool",
            state=ResultState.SUCCESS,
            trace=TraceContext.root(),
            summary=" ",
        )

def test_tool_execution_result_preserves_action_id() -> None:
    action_id = new_action_id()

    result = ToolExecutionResult(
        action_id=action_id,
        attempt_id=new_attempt_id(),
        tool_name="test_tool",
        state=ResultState.SUCCESS,
        trace=TraceContext.root(),
        summary="Result.",
    )

    assert result.action_id == action_id

def test_tool_execution_result_preserves_attempt_id() -> None:
    attempt_id = new_attempt_id()

    result = ToolExecutionResult(
        action_id=new_action_id(),
        attempt_id=attempt_id,
        tool_name="test_tool",
        state=ResultState.SUCCESS,
        trace=TraceContext.root(),
        summary="Result.",
    )

    assert result.attempt_id == attempt_id