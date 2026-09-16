from typing import Protocol, runtime_checkable

from ayeon.contracts.action_attempt import ActionAttempt
from ayeon.contracts.authorized_action import AuthorizedAction
from ayeon.contracts.tool_execution import ToolExecutionResult
from ayeon.tools.adapter import ToolAdapter


def test_tool_adapter_is_protocol() -> None:
    assert issubclass(ToolAdapter, Protocol)


def test_tool_adapter_is_runtime_checkable() -> None:
    @runtime_checkable
    class ExampleProtocol(Protocol):
        pass

    assert getattr(ToolAdapter, "_is_runtime_protocol", False)
    assert getattr(ExampleProtocol, "_is_runtime_protocol", False)


def test_fake_tool_satisfies_adapter_contract() -> None:
    class FakeTool:
        @property
        def name(self) -> str:
            return "fake_tool"

        def execute(
            self,
            authorized_action: AuthorizedAction,
            attempt: ActionAttempt,
        ) -> ToolExecutionResult:
            raise NotImplementedError

    assert isinstance(FakeTool(), ToolAdapter)