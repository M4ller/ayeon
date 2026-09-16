"""Deterministic lifecycle transition policy for Ayeon Core."""

from __future__ import annotations

from ayeon.contracts.lifecycle import LifecycleState


class LifecyclePolicy:
    """Defines which runtime lifecycle transitions are allowed."""

    _ALLOWED_TRANSITIONS: dict[LifecycleState, frozenset[LifecycleState]] = {
        LifecycleState.STOPPED: frozenset({
            LifecycleState.BOOTING,
        }),
        LifecycleState.BOOTING: frozenset({
            LifecycleState.VERIFYING,
            LifecycleState.SAFE_MODE,
            LifecycleState.FAILED,
            LifecycleState.SHUTTING_DOWN,
        }),
        LifecycleState.VERIFYING: frozenset({
            LifecycleState.RUNNING,
            LifecycleState.DEGRADED,
            LifecycleState.SAFE_MODE,
            LifecycleState.FAILED,
            LifecycleState.SHUTTING_DOWN,
        }),
        LifecycleState.RUNNING: frozenset({
            LifecycleState.DEGRADED,
            LifecycleState.SAFE_MODE,
            LifecycleState.SHUTTING_DOWN,
            LifecycleState.FAILED,
        }),
        LifecycleState.DEGRADED: frozenset({
            LifecycleState.RUNNING,
            LifecycleState.SAFE_MODE,
            LifecycleState.RECOVERING,
            LifecycleState.SHUTTING_DOWN,
            LifecycleState.FAILED,
        }),
        LifecycleState.SAFE_MODE: frozenset({
            LifecycleState.RECOVERING,
            LifecycleState.SHUTTING_DOWN,
            LifecycleState.FAILED,
        }),
        LifecycleState.RECOVERING: frozenset({
            LifecycleState.VERIFYING,
            LifecycleState.SAFE_MODE,
            LifecycleState.FAILED,
            LifecycleState.SHUTTING_DOWN,
        }),
        LifecycleState.SHUTTING_DOWN: frozenset({
            LifecycleState.STOPPED,
            LifecycleState.FAILED,
        }),
        LifecycleState.FAILED: frozenset({
            LifecycleState.RECOVERING,
            LifecycleState.SHUTTING_DOWN,
        }),
    }

    @classmethod
    def can_transition(
        cls,
        current: LifecycleState,
        target: LifecycleState,
    ) -> bool:
        """Return whether a lifecycle transition is permitted."""

        return target in cls._ALLOWED_TRANSITIONS.get(current, frozenset())
