"""Resolved action execution association contracts for Ayeon Core."""

from __future__ import annotations

from dataclasses import dataclass

from ayeon.contracts.action_execution_verification import (
    ActionExecutionVerification,
)
from ayeon.contracts.action_outcome import ActionOutcome


@dataclass(frozen=True, slots=True)
class ResolvedActionExecution:
    """Associate verified execution evidence with its final outcome.

    This contract proves association consistency only.
    It does not decide or modify the final outcome.
    """

    verified_execution: ActionExecutionVerification
    outcome: ActionOutcome

    def __post_init__(self) -> None:
        attempt = self.verified_execution.execution.attempt

        if self.outcome.action_id != attempt.action_id:
            raise ValueError(
                "outcome action_id must match execution action_id"
            )

        if self.outcome.attempt_id != attempt.attempt_id:
            raise ValueError(
                "outcome attempt_id must match execution attempt_id"
            )

        if (
            self.outcome.trace.correlation_id
            != attempt.trace.correlation_id
        ):
            raise ValueError(
                "outcome correlation must match execution correlation"
            )