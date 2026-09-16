"""Action verification interface for Ayeon Core."""

from __future__ import annotations

from typing import Protocol, runtime_checkable

from ayeon.contracts.action_execution import ActionExecution
from ayeon.contracts.action_verification import ActionVerificationResult


@runtime_checkable
class ActionVerifier(Protocol):
    """Interface implemented by action effect verifiers."""

    @property
    def name(self) -> str:
        """Return the canonical verifier name."""
        ...

    def verify(
        self,
        execution: ActionExecution,
    ) -> ActionVerificationResult:
        """Verify the external effect of one action execution attempt."""
        ...