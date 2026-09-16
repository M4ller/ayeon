"""Authorized action pipeline orchestration for Ayeon Core."""

from __future__ import annotations

from ayeon.contracts.authorized_action import AuthorizedAction
from ayeon.contracts.resolved_action_execution import ResolvedActionExecution
from ayeon.runtime.outcome_resolver import OutcomeResolver
from ayeon.tools.manager import ToolManager
from ayeon.verification.manager import VerificationManager


class ActionPipeline:
    """Coordinate an authorized action through execution and verification.

    This pipeline does not authorize actions, execute tools directly,
    verify effects itself, or decide final outcome semantics.
    """

    def __init__(
        self,
        *,
        tool_manager: ToolManager,
        verification_manager: VerificationManager,
        outcome_resolver: OutcomeResolver,
    ) -> None:
        self._tool_manager = tool_manager
        self._verification_manager = verification_manager
        self._outcome_resolver = outcome_resolver

    def run(
        self,
        authorized_action: AuthorizedAction,
    ) -> ResolvedActionExecution:
        """Run one already-authorized action through the action pipeline."""

        execution = self._tool_manager.execute(authorized_action)

        verified_execution = self._verification_manager.verify(
            execution
        )

        return self._outcome_resolver.resolve(
            verified_execution
        )