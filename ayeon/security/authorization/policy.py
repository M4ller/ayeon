"""Deterministic authorization policy for Ayeon Core."""

from __future__ import annotations

from collections.abc import Iterable

from ayeon.contracts.approval import ApprovalEvidence
from ayeon.contracts.authorization import (
    AuthorizationDecision,
    AuthorizationOutcome,
    AuthorizationRequest,
)

AUTHORIZATION_POLICY_SOURCE = "authorization_policy"


class AuthorizationPolicy:
    """Evaluate authorization requests without executing actions."""

    def __init__(
        self,
        *,
        approval_authorities: Iterable[str] = (),
    ) -> None:
        authorities = {
            authority.strip()
            for authority in approval_authorities
            if authority.strip()
        }
        self._approval_authorities = frozenset(authorities)

    def evaluate(
        self,
        request: AuthorizationRequest,
        *,
        approval: ApprovalEvidence | None = None,
    ) -> AuthorizationDecision:
        """Return the deterministic authorization decision for a request."""

        if (
            approval is not None
            and approval.approved_by in self._approval_authorities
            and approval.action_id == request.action.action_id
            and approval.trace.correlation_id
            == request.trace.correlation_id
        ):
            return AuthorizationDecision(
                action_id=request.action.action_id,
                outcome=AuthorizationOutcome.ALLOW,
                decided_by=AUTHORIZATION_POLICY_SOURCE,
                trace=request.trace,
                reason="Matching approval from an authorized authority was provided.",
            )

        return AuthorizationDecision(
            action_id=request.action.action_id,
            outcome=AuthorizationOutcome.REQUIRE_APPROVAL,
            decided_by=AUTHORIZATION_POLICY_SOURCE,
            trace=request.trace,
            reason="Explicit approval from an authorized authority is required.",
        )