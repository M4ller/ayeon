"""Tool manager for Ayeon Core."""

from __future__ import annotations

from collections.abc import Iterable

from ayeon.contracts.action_attempt import ActionAttempt
from ayeon.contracts.action_execution import ActionExecution
from ayeon.contracts.authorized_action import AuthorizedAction
from ayeon.contracts.common import ResultState
from ayeon.contracts.tool_execution import ToolExecutionResult
from ayeon.tools.adapter import ToolAdapter


class ToolNotFoundError(LookupError):
    """Raised when no registered adapter matches an authorized action."""


class DuplicateToolError(ValueError):
    """Raised when multiple adapters use the same canonical tool name."""


class ToolManager:
    """Coordinate authorized actions with operational tool adapters."""

    def __init__(
        self,
        *,
        tools: Iterable[ToolAdapter],
    ) -> None:
        registered: dict[str, ToolAdapter] = {}

        for tool in tools:
            tool_name = tool.name

            if not tool_name.strip():
                raise ValueError("tool name must not be empty")

            if tool_name in registered:
                raise DuplicateToolError(
                    f"Duplicate tool name: {tool_name}"
                )

            registered[tool_name] = tool

        self._tools = registered

    def execute(
        self,
        authorized_action: AuthorizedAction,
    ) -> ActionExecution:
        """Attempt an authorized action using its matching tool adapter."""

        action = authorized_action.action
        tool = self._tools.get(action.action_type)

        if tool is None:
            raise ToolNotFoundError(
                f"No registered tool for action type: {action.action_type}"
            )

        attempt = ActionAttempt(
            action_id=action.action_id,
            tool_name=tool.name,
            trace=action.trace,
        )

        try:
            result = tool.execute(
                authorized_action,
                attempt,
            )
        except Exception as exc:
            result = ToolExecutionResult(
                action_id=action.action_id,
                attempt_id=attempt.attempt_id,
                tool_name=tool.name,
                state=ResultState.UNKNOWN,
                trace=attempt.trace,
                summary=(
                    "Tool adapter raised an exception; "
                    f"external effect is unknown: {type(exc).__name__}"
                ),
            )

        return ActionExecution(
            authorized_action=authorized_action,
            attempt=attempt,
            result=result,
        )