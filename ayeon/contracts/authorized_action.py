"""Authorized action contracts for Ayeon Core."""

from __future__ import annotations

from dataclasses import dataclass

from ayeon.contracts.actions import ActionIntent
from ayeon.contracts.authorization import (
    AuthorizationDecision,
    AuthorizationOutcome,
)


@dataclass(frozen=True, slots=True)
class AuthorizedAction:
    """Action intent paired with a valid ALLOW authorization decision.

    This object represents execution eligibility only.
    It does not execute the action and does not imply execution success.
    """

    action: ActionIntent
    authorization: AuthorizationDecision

    def __post_init__(self) -> None:
        if self.authorization.outcome is not AuthorizationOutcome.ALLOW:
            raise ValueError(
                "authorization outcome must be ALLOW"
            )

        if self.authorization.action_id != self.action.action_id:
            raise ValueError(
                "authorization action_id must match action action_id"
            )

        if (
            self.authorization.trace.correlation_id
            != self.action.trace.correlation_id
        ):
            raise ValueError(
                "authorization correlation must match action correlation"
            )