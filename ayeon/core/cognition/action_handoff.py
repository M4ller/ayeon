"""Cognitive action handoff for Ayeon Core."""

from __future__ import annotations

from ayeon.contracts.authorization import AuthorizationRequest
from ayeon.contracts.cognition import CognitiveOutput
from ayeon.runtime.executive import Executive


class CognitiveActionHandoff:
    """Hand cognitive action proposals to the executive boundary.

    The handoff converts proposed action intents into authorization requests.
    It does not authorize actions, execute tools, or process non-action
    cognitive output.
    """

    def __init__(
        self,
        *,
        executive: Executive,
    ) -> None:
        self._executive = executive

    def prepare_authorization_requests(
        self,
        output: CognitiveOutput,
    ) -> tuple[AuthorizationRequest, ...]:
        """Prepare authorization requests for proposed cognitive actions."""

        return tuple(
            self._executive.request_authorization(action)
            for action in output.action_intents
        )
