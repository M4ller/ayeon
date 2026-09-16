"""Action execution association contracts for Ayeon Core."""

from __future__ import annotations

from dataclasses import dataclass

from ayeon.contracts.action_attempt import ActionAttempt
from ayeon.contracts.authorized_action import AuthorizedAction
from ayeon.contracts.tool_execution import ToolExecutionResult


@dataclass(frozen=True, slots=True)
class ActionExecution:
    """Associate an authorized action, attempt, and reported tool result.

    This contract proves chain consistency only.
    It does not imply independent verification or completion.
    """

    authorized_action: AuthorizedAction
    attempt: ActionAttempt
    result: ToolExecutionResult

    def __post_init__(self) -> None:
        action = self.authorized_action.action

        if self.attempt.action_id != action.action_id:
            raise ValueError(
                "attempt action_id must match authorized action action_id"
            )

        if self.result.action_id != action.action_id:
            raise ValueError(
                "result action_id must match authorized action action_id"
            )

        if self.result.attempt_id != self.attempt.attempt_id:
            raise ValueError(
                "result attempt_id must match action attempt attempt_id"
            )

        if self.result.tool_name != self.attempt.tool_name:
            raise ValueError(
                "result tool_name must match action attempt tool_name"
            )

        if (
            self.attempt.trace.correlation_id
            != action.trace.correlation_id
        ):
            raise ValueError(
                "attempt correlation must match authorized action correlation"
            )

        if (
            self.result.trace.correlation_id
            != self.attempt.trace.correlation_id
        ):
            raise ValueError(
                "result correlation must match action attempt correlation"
            )