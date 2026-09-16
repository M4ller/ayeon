"""Supervisor Runtime for Ayeon Core."""

from __future__ import annotations

from ayeon.contracts.common import TraceContext
from ayeon.contracts.events import AyeonEvent, EventPersistence
from ayeon.contracts.health import HealthReport
from ayeon.contracts.lifecycle import LifecycleState, LifecycleTransition
from ayeon.contracts.runtime_state import RuntimeStateView
from ayeon.contracts.verification import VerificationResult, VerificationState
from ayeon.runtime.event_bus import EventBus
from ayeon.runtime.health import RuntimeHealth
from ayeon.runtime.lifecycle_policy import LifecyclePolicy

LIFECYCLE_TRANSITIONED = "runtime.lifecycle_transitioned"
SUPERVISOR_SOURCE = "runtime.supervisor"


class InvalidLifecycleTransitionError(RuntimeError):
    """Raised when the runtime rejects an invalid lifecycle transition."""


class VerificationRequiredError(RuntimeError):
    """Raised when RUNNING is requested without required verification."""


class SupervisorRuntime:
    """Owns and controls Ayeon's runtime lifecycle state."""

    _REQUIRED_VERIFICATIONS = frozenset({
        "identity",
        "continuity",
    })

    def __init__(self, event_bus: EventBus | None = None) -> None:
        self._state = LifecycleState.STOPPED
        self._last_transition: LifecycleTransition | None = None
        self._health = RuntimeHealth()
        self._verifications: dict[str, VerificationResult] = {}
        self._event_bus = event_bus

    @property
    def state(self) -> LifecycleState:
        """Return the current runtime lifecycle state."""

        return self._state

    @property
    def last_transition(self) -> LifecycleTransition | None:
        """Return the most recently completed lifecycle transition."""

        return self._last_transition

    @property
    def health(self) -> RuntimeHealth:
        """Return the runtime health owner."""

        return self._health

    def state_view(self) -> RuntimeStateView:
        """Return an immutable view of current runtime state."""

        return RuntimeStateView(
            lifecycle=self._state,
            health=self._health.overall,
            health_reports=self._health.reports,
            has_critical_failure=self._health.has_critical_failure,
        )
    def record_verification(self, result: VerificationResult) -> None:
        """Record the latest verification result for one subject."""

        self._verifications[result.subject] = result

    def verification(self, subject: str) -> VerificationResult | None:
        """Return the latest verification result for one subject."""

        return self._verifications.get(subject)

    def _required_verifications_passed(self) -> bool:
        return all(
            (
                result := self._verifications.get(subject)
            ) is not None
            and result.state is VerificationState.VERIFIED
            for subject in self._REQUIRED_VERIFICATIONS
        )

    def transition_to(
        self,
        target: LifecycleState,
        *,
        reason: str,
        initiated_by: str,
        trace: TraceContext,
    ) -> LifecycleTransition:
        """Validate and perform one lifecycle state transition."""

        previous = self._state

        if not LifecyclePolicy.can_transition(previous, target):
            raise InvalidLifecycleTransitionError(
                f"invalid lifecycle transition: {previous.value} -> {target.value}"
            )

        if (
            previous is LifecycleState.VERIFYING
            and target is LifecycleState.RUNNING
            and not self._required_verifications_passed()
        ):
            raise VerificationRequiredError(
                "identity and continuity must be verified before RUNNING"
            )

        transition = LifecycleTransition(
            previous=previous,
            target=target,
            reason=reason,
            initiated_by=initiated_by,
            trace=trace,
        )

        if (
            previous is LifecycleState.STOPPED
            and target is LifecycleState.BOOTING
        ):
            self._verifications.clear()

        self._state = target
        self._last_transition = transition

        if self._event_bus is not None:
            self._event_bus.publish(
                AyeonEvent(
                    event_type=LIFECYCLE_TRANSITIONED,
                    source=SUPERVISOR_SOURCE,
                    trace=trace,
                    persistence=EventPersistence.AUDIT,
                    payload={
                        "previous": previous.value,
                        "target": target.value,
                        "reason": reason,
                        "initiated_by": initiated_by,
                    },
                )
            )

        return transition

    def report_health(self, report: HealthReport) -> None:
        """Record a component health observation."""

        self._health.report(report)

    def evaluate_health(
        self,
        *,
        trace: TraceContext,
    ) -> LifecycleTransition | None:
        """Apply lifecycle protection required by current health."""

        if not self._health.has_critical_failure:
            return None

        if self._state is LifecycleState.SAFE_MODE:
            return None

        if not LifecyclePolicy.can_transition(
            self._state,
            LifecycleState.SAFE_MODE,
        ):
            return None

        return self.transition_to(
            LifecycleState.SAFE_MODE,
            reason="Critical runtime component failure detected.",
            initiated_by="runtime_health",
            trace=trace,
        )
