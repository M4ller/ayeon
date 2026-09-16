"""Verified action execution association contracts for Ayeon Core."""

from __future__ import annotations

from dataclasses import dataclass

from ayeon.contracts.action_execution import ActionExecution
from ayeon.contracts.action_verification import ActionVerificationResult


@dataclass(frozen=True, slots=True)
class ActionExecutionVerification:
    """Associate one action execution with its verification result.

    This contract proves association consistency only.
    The verification state may be VERIFIED, FAILED, or UNKNOWN.
    """

    execution: ActionExecution
    verification: ActionVerificationResult

    def __post_init__(self) -> None:
        attempt = self.execution.attempt

        if self.verification.action_id != attempt.action_id:
            raise ValueError(
                "verification action_id must match execution action_id"
            )

        if self.verification.attempt_id != attempt.attempt_id:
            raise ValueError(
                "verification attempt_id must match execution attempt_id"
            )

        if (
            self.verification.trace.correlation_id
            != attempt.trace.correlation_id
        ):
            raise ValueError(
                "verification correlation must match execution correlation"
            )