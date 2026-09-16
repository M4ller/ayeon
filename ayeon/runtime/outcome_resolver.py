"""Deterministic final action outcome resolution for Ayeon Core."""

from __future__ import annotations

from ayeon.contracts.action_execution_verification import (
    ActionExecutionVerification,
)
from ayeon.contracts.action_outcome import ActionOutcome
from ayeon.contracts.common import ResultState
from ayeon.contracts.resolved_action_execution import ResolvedActionExecution
from ayeon.contracts.verification import VerificationState


class OutcomeResolver:
    """Resolve final action state from execution and verification evidence."""

    name = "outcome_resolver"

    def resolve(
        self,
        evidence: ActionExecutionVerification,
    ) -> ResolvedActionExecution:
        tool_state = evidence.execution.result.state
        verification_state = evidence.verification.state

        if tool_state is ResultState.FAILED:
            final_state = ResultState.FAILED
            reason = "Tool execution reported failure."

        elif tool_state is ResultState.UNKNOWN:
            final_state = ResultState.UNKNOWN
            reason = "Tool execution result is unknown."

        elif verification_state is VerificationState.VERIFIED:
            final_state = ResultState.SUCCESS
            reason = (
                "Tool reported success and external effect was verified."
            )

        elif verification_state is VerificationState.FAILED:
            final_state = ResultState.FAILED
            reason = (
                "Tool reported success but external effect verification failed."
            )

        else:
            final_state = ResultState.UNKNOWN
            reason = (
                "Tool reported success but external effect remains unknown."
            )

        attempt = evidence.execution.attempt

        outcome = ActionOutcome(
            action_id=attempt.action_id,
            attempt_id=attempt.attempt_id,
            state=final_state,
            resolved_by=self.name,
            trace=attempt.trace,
            reason=reason,
        )

        return ResolvedActionExecution(
            verified_execution=evidence,
            outcome=outcome,
        )