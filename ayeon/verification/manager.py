"""Action verification manager for Ayeon Core."""

from __future__ import annotations

from collections.abc import Iterable

from ayeon.contracts.action_execution import ActionExecution
from ayeon.contracts.action_execution_verification import (
    ActionExecutionVerification,
)
from ayeon.contracts.action_verification import ActionVerificationResult
from ayeon.contracts.verification import VerificationState
from ayeon.verification.verifier import ActionVerifier


class VerifierNotFoundError(LookupError):
    """Raised when no registered verifier matches an action execution."""


class DuplicateVerifierError(ValueError):
    """Raised when multiple verifiers use the same canonical name."""


class VerificationManager:
    """Coordinate action executions with effect verifiers."""

    def __init__(
        self,
        *,
        verifiers: Iterable[ActionVerifier],
    ) -> None:
        registered: dict[str, ActionVerifier] = {}

        for verifier in verifiers:
            verifier_name = verifier.name

            if not verifier_name.strip():
                raise ValueError("verifier name must not be empty")

            if verifier_name in registered:
                raise DuplicateVerifierError(
                    f"Duplicate verifier name: {verifier_name}"
                )

            registered[verifier_name] = verifier

        self._verifiers = registered

    def verify(
        self,
        execution: ActionExecution,
    ) -> ActionExecutionVerification:
        """Verify one action execution using its matching verifier."""

        verifier = self._verifiers.get(execution.attempt.tool_name)

        if verifier is None:
            raise VerifierNotFoundError(
                "No registered verifier for tool: "
                f"{execution.attempt.tool_name}"
            )

        try:
            verification = verifier.verify(execution)
        except Exception as exc:
            verification = ActionVerificationResult(
                action_id=execution.attempt.action_id,
                attempt_id=execution.attempt.attempt_id,
                state=VerificationState.UNKNOWN,
                verified_by=verifier.name,
                trace=execution.attempt.trace,
                reason=(
                    "Verifier raised an exception; "
                    f"effect verification is unknown: {type(exc).__name__}"
                ),
            )

        if verification.verified_by != verifier.name:
            raise ValueError(
                "verification verified_by must match selected verifier"
            )

        return ActionExecutionVerification(
            execution=execution,
            verification=verification,
        )