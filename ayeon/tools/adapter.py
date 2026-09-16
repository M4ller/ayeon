"""Tool adapter interface for Ayeon Core."""

from __future__ import annotations

from typing import Protocol, runtime_checkable

from ayeon.contracts.action_attempt import ActionAttempt
from ayeon.contracts.authorized_action import AuthorizedAction
from ayeon.contracts.tool_execution import ToolExecutionResult


@runtime_checkable
class ToolAdapter(Protocol):
    """Interface implemented by operational tool adapters."""

    @property
    def name(self) -> str:
        """Return the canonical tool name."""
        ...

    def execute(
        self,
        authorized_action: AuthorizedAction,
        attempt: ActionAttempt,
    ) -> ToolExecutionResult:
        """Attempt execution and return the tool-reported result."""
        ...