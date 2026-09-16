"""Executive boundary for Ayeon Core."""

from __future__ import annotations

from ayeon.contracts.actions import ActionIntent
from ayeon.contracts.authorization import (
    AuthorizationDecision,
    AuthorizationRequest,
)
from ayeon.contracts.authorized_action import AuthorizedAction


class Executive:
    """Coordinates action intents without authorizing or executing them."""

    def request_authorization(
        self,
        action: ActionIntent,
    ) -> AuthorizationRequest:
        """Create an authorization request for an action intent."""

        return AuthorizationRequest(
            action=action,
            trace=action.trace,
        )

    def materialize_authorized_action(
        self,
        *,
        action: ActionIntent,
        decision: AuthorizationDecision,
    ) -> AuthorizedAction:
        """Materialize execution eligibility from an authorization decision."""

        return AuthorizedAction(
            action=action,
            authorization=decision,
        )