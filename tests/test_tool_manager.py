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
from ayeon.tools.manager import (
    DuplicateToolError,
    ToolManager,
    ToolNotFoundError,
)


def make_authorized_action() -> AuthorizedAction:
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
        reason="Authorized for tool manager test.",
    )

    return AuthorizedAction(
        action=action,
        authorization=decision,
    )


class FakeTool:
    def __init__(self) -> None:
        self.calls = 0

    @property
    def name(self) -> str:
        return "fake_tool"

    def execute(
        self,
        authorized_action: AuthorizedAction,
        attempt: ActionAttempt,
    ) -> ToolExecutionResult:
        self.calls += 1

        return ToolExecutionResult(
            action_id=authorized_action.action.action_id,
            attempt_id=attempt.attempt_id,
            tool_name=self.name,
            state=ResultState.SUCCESS,
            trace=attempt.trace,
            summary="Fake tool reported success.",
        )


def test_tool_manager_executes_authorized_action() -> None:
    tool = FakeTool()
    manager = ToolManager(tools=[tool])
    authorized = make_authorized_action()

    execution = manager.execute(authorized)

    assert isinstance(execution, ActionExecution)
    assert execution.authorized_action is authorized
    assert execution.attempt.action_id == authorized.action.action_id
    assert execution.attempt.tool_name == tool.name
    assert execution.result.attempt_id == execution.attempt.attempt_id
    assert tool.calls == 1

def test_tool_manager_rejects_unregistered_tool() -> None:
    tool = FakeTool()
    manager = ToolManager(tools=[tool])

    action = ActionIntent(
        action_type="missing_tool",
        requested_by="cognition",
        trace=TraceContext.root(),
    )

    decision = AuthorizationDecision(
        action_id=action.action_id,
        outcome=AuthorizationOutcome.ALLOW,
        decided_by="authorization_policy",
        trace=action.trace,
        reason="Authorized for missing tool test.",
    )

    authorized = AuthorizedAction(
        action=action,
        authorization=decision,
    )

    try:
        manager.execute(authorized)
    except ToolNotFoundError as exc:
        assert "missing_tool" in str(exc)
    else:
        raise AssertionError("Unregistered tool must not be executed")

    assert tool.calls == 0

def test_tool_manager_rejects_duplicate_tool_names() -> None:
    first = FakeTool()
    second = FakeTool()

    try:
        ToolManager(tools=[first, second])
    except DuplicateToolError as exc:
        assert "fake_tool" in str(exc)
    else:
        raise AssertionError("Duplicate tool names must be rejected")

    assert first.calls == 0
    assert second.calls == 0

class ExplodingTool:
    @property
    def name(self) -> str:
        return "exploding_tool"

    def execute(
        self,
        authorized_action: AuthorizedAction,
        attempt: ActionAttempt,
    ) -> ToolExecutionResult:
        raise RuntimeError("Simulated adapter failure")


def test_tool_manager_converts_adapter_exception_to_unknown() -> None:
    tool = ExplodingTool()
    manager = ToolManager(tools=[tool])

    action = ActionIntent(
        action_type="exploding_tool",
        requested_by="cognition",
        trace=TraceContext.root(),
    )

    decision = AuthorizationDecision(
        action_id=action.action_id,
        outcome=AuthorizationOutcome.ALLOW,
        decided_by="authorization_policy",
        trace=action.trace,
        reason="Authorized for exception test.",
    )

    authorized = AuthorizedAction(
        action=action,
        authorization=decision,
    )

    execution = manager.execute(authorized)

    assert execution.authorized_action is authorized
    assert execution.attempt.action_id == action.action_id
    assert execution.attempt.tool_name == tool.name
    assert execution.result.action_id == action.action_id
    assert execution.result.attempt_id == execution.attempt.attempt_id
    assert execution.result.state is ResultState.UNKNOWN

class InconsistentTool:
    @property
    def name(self) -> str:
        return "inconsistent_tool"

    def execute(
        self,
        authorized_action: AuthorizedAction,
        attempt: ActionAttempt,
    ) -> ToolExecutionResult:
        from ayeon.contracts.common import new_attempt_id

        return ToolExecutionResult(
            action_id=authorized_action.action.action_id,
            attempt_id=new_attempt_id(),
            tool_name=self.name,
            state=ResultState.SUCCESS,
            trace=attempt.trace,
            summary="Inconsistent fake result.",
        )


def test_tool_manager_rejects_inconsistent_tool_result() -> None:
    tool = InconsistentTool()
    manager = ToolManager(tools=[tool])

    action = ActionIntent(
        action_type="inconsistent_tool",
        requested_by="cognition",
        trace=TraceContext.root(),
    )

    decision = AuthorizationDecision(
        action_id=action.action_id,
        outcome=AuthorizationOutcome.ALLOW,
        decided_by="authorization_policy",
        trace=action.trace,
        reason="Authorized for inconsistent result test.",
    )

    authorized = AuthorizedAction(
        action=action,
        authorization=decision,
    )

    try:
        manager.execute(authorized)
    except ValueError as exc:
        assert "attempt_id" in str(exc)
    else:
        raise AssertionError(
            "Inconsistent tool result must not become ActionExecution"
        )

class BlankNameTool:
    @property
    def name(self) -> str:
        return "   "

    def execute(
        self,
        authorized_action: AuthorizedAction,
        attempt: ActionAttempt,
    ) -> ToolExecutionResult:
        raise AssertionError("Blank-name tool must never execute")


def test_tool_manager_rejects_blank_tool_name() -> None:
    tool = BlankNameTool()

    try:
        ToolManager(tools=[tool])
    except ValueError as exc:
        assert "name" in str(exc)
    else:
        raise AssertionError("Blank tool name must be rejected")