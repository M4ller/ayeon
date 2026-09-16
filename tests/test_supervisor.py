import pytest

from ayeon.contracts.common import HealthState, TraceContext
from ayeon.contracts.health import ComponentCriticality, HealthReport
from ayeon.contracts.lifecycle import LifecycleState
from ayeon.contracts.verification import VerificationResult, VerificationState
from ayeon.runtime.supervisor import (
    InvalidLifecycleTransitionError,
    SupervisorRuntime,
    VerificationRequiredError,
)


def verified_result(subject: str, trace: TraceContext) -> VerificationResult:
    return VerificationResult(
        subject=subject,
        state=VerificationState.VERIFIED,
        verified_by=f"{subject}_verifier",
        trace=trace,
        reason=f"{subject} verified.",
    )


def bring_to_verifying(
    runtime: SupervisorRuntime,
    trace: TraceContext,
) -> None:
    runtime.transition_to(
        LifecycleState.BOOTING,
        reason="Startup requested.",
        initiated_by="runtime",
        trace=trace,
    )
    runtime.transition_to(
        LifecycleState.VERIFYING,
        reason="Begin verification.",
        initiated_by="runtime",
        trace=trace,
    )


def bring_to_running(
    runtime: SupervisorRuntime,
    trace: TraceContext,
) -> None:
    bring_to_verifying(runtime, trace)

    runtime.record_verification(verified_result("identity", trace))
    runtime.record_verification(verified_result("continuity", trace))

    runtime.transition_to(
        LifecycleState.RUNNING,
        reason="Required verification completed.",
        initiated_by="runtime",
        trace=trace,
    )


def test_supervisor_starts_stopped() -> None:
    runtime = SupervisorRuntime()

    assert runtime.state is LifecycleState.STOPPED
    assert runtime.last_transition is None


def test_supervisor_performs_valid_transition() -> None:
    runtime = SupervisorRuntime()
    trace = TraceContext.root()

    transition = runtime.transition_to(
        LifecycleState.BOOTING,
        reason="Startup requested.",
        initiated_by="runtime",
        trace=trace,
    )

    assert runtime.state is LifecycleState.BOOTING
    assert runtime.last_transition is transition


def test_supervisor_rejects_invalid_transition() -> None:
    runtime = SupervisorRuntime()

    with pytest.raises(
        InvalidLifecycleTransitionError,
        match="stopped -> running",
    ):
        runtime.transition_to(
            LifecycleState.RUNNING,
            reason="Attempt to skip boot.",
            initiated_by="runtime",
            trace=TraceContext.root(),
        )


def test_rejected_transition_does_not_mutate_state() -> None:
    runtime = SupervisorRuntime()

    with pytest.raises(InvalidLifecycleTransitionError):
        runtime.transition_to(
            LifecycleState.RUNNING,
            reason="Invalid transition.",
            initiated_by="runtime",
            trace=TraceContext.root(),
        )

    assert runtime.state is LifecycleState.STOPPED
    assert runtime.last_transition is None


def test_running_requires_verification() -> None:
    runtime = SupervisorRuntime()
    trace = TraceContext.root()

    bring_to_verifying(runtime, trace)

    with pytest.raises(
        VerificationRequiredError,
        match="identity and continuity must be verified",
    ):
        runtime.transition_to(
            LifecycleState.RUNNING,
            reason="Attempt without verification.",
            initiated_by="runtime",
            trace=trace,
        )

    assert runtime.state is LifecycleState.VERIFYING


def test_identity_only_is_not_enough() -> None:
    runtime = SupervisorRuntime()
    trace = TraceContext.root()

    bring_to_verifying(runtime, trace)
    runtime.record_verification(verified_result("identity", trace))

    with pytest.raises(VerificationRequiredError):
        runtime.transition_to(
            LifecycleState.RUNNING,
            reason="Continuity missing.",
            initiated_by="runtime",
            trace=trace,
        )


def test_unknown_continuity_blocks_running() -> None:
    runtime = SupervisorRuntime()
    trace = TraceContext.root()

    bring_to_verifying(runtime, trace)
    runtime.record_verification(verified_result("identity", trace))
    runtime.record_verification(
        VerificationResult(
            subject="continuity",
            state=VerificationState.UNKNOWN,
            verified_by="continuity_verifier",
            trace=trace,
            reason="Continuity could not be established.",
        )
    )

    with pytest.raises(VerificationRequiredError):
        runtime.transition_to(
            LifecycleState.RUNNING,
            reason="Attempt with uncertain continuity.",
            initiated_by="runtime",
            trace=trace,
        )


def test_verified_identity_and_continuity_allow_running() -> None:
    runtime = SupervisorRuntime()
    trace = TraceContext.root()

    bring_to_running(runtime, trace)

    assert runtime.state is LifecycleState.RUNNING


def test_optional_failure_does_not_force_safe_mode() -> None:
    runtime = SupervisorRuntime()
    trace = TraceContext.root()

    bring_to_running(runtime, trace)

    runtime.report_health(
        HealthReport(
            component="camera",
            state=HealthState.FAILED,
            criticality=ComponentCriticality.OPTIONAL,
            reason="Camera disconnected.",
        )
    )

    transition = runtime.evaluate_health(trace=trace)

    assert transition is None
    assert runtime.state is LifecycleState.RUNNING


def test_critical_failure_forces_safe_mode() -> None:
    runtime = SupervisorRuntime()
    trace = TraceContext.root()

    bring_to_running(runtime, trace)

    runtime.report_health(
        HealthReport(
            component="identity",
            state=HealthState.FAILED,
            criticality=ComponentCriticality.CRITICAL,
            reason="Identity integrity verification failed.",
        )
    )

    transition = runtime.evaluate_health(trace=trace)

    assert transition is not None
    assert transition.target is LifecycleState.SAFE_MODE
    assert runtime.state is LifecycleState.SAFE_MODE


def test_repeated_critical_evaluation_does_not_fake_transition() -> None:
    runtime = SupervisorRuntime()
    trace = TraceContext.root()

    runtime.transition_to(
        LifecycleState.BOOTING,
        reason="Startup requested.",
        initiated_by="runtime",
        trace=trace,
    )

    runtime.report_health(
        HealthReport(
            component="continuity",
            state=HealthState.FAILED,
            criticality=ComponentCriticality.CRITICAL,
            reason="Continuity verification failed.",
        )
    )

    first = runtime.evaluate_health(trace=trace)
    second = runtime.evaluate_health(trace=trace)

    assert first is not None
    assert first.target is LifecycleState.SAFE_MODE
    assert second is None
    assert runtime.last_transition is first

def test_new_boot_invalidates_previous_verifications() -> None:
    runtime = SupervisorRuntime()
    trace = TraceContext.root()

    bring_to_running(runtime, trace)

    assert runtime.verification("identity") is not None
    assert runtime.verification("continuity") is not None

    runtime.transition_to(
        LifecycleState.SHUTTING_DOWN,
        reason="Shutdown requested.",
        initiated_by="runtime",
        trace=trace,
    )
    runtime.transition_to(
        LifecycleState.STOPPED,
        reason="Shutdown completed.",
        initiated_by="runtime",
        trace=trace,
    )
    runtime.transition_to(
        LifecycleState.BOOTING,
        reason="New startup requested.",
        initiated_by="runtime",
        trace=trace,
    )

    assert runtime.verification("identity") is None
    assert runtime.verification("continuity") is None

    runtime.transition_to(
        LifecycleState.VERIFYING,
        reason="Begin new verification cycle.",
        initiated_by="runtime",
        trace=trace,
    )

    with pytest.raises(VerificationRequiredError):
        runtime.transition_to(
            LifecycleState.RUNNING,
            reason="Attempt to reuse previous verification.",
            initiated_by="runtime",
            trace=trace,
        )

    assert runtime.state is LifecycleState.VERIFYING

def test_valid_transition_emits_lifecycle_audit_event() -> None:
    from ayeon.contracts.events import EventPersistence
    from ayeon.runtime.event_bus import EventBus
    from ayeon.runtime.supervisor import LIFECYCLE_TRANSITIONED

    bus = EventBus()
    events = []
    bus.subscribe(LIFECYCLE_TRANSITIONED, events.append)

    runtime = SupervisorRuntime(event_bus=bus)
    trace = TraceContext.root()

    runtime.transition_to(
        LifecycleState.BOOTING,
        reason="Startup requested.",
        initiated_by="runtime",
        trace=trace,
    )

    assert len(events) == 1

    event = events[0]

    assert event.event_type == LIFECYCLE_TRANSITIONED
    assert event.persistence is EventPersistence.AUDIT
    assert event.payload["previous"] == "stopped"
    assert event.payload["target"] == "booting"
    assert event.payload["reason"] == "Startup requested."
    assert event.payload["initiated_by"] == "runtime"


def test_lifecycle_event_preserves_correlation() -> None:
    from ayeon.runtime.event_bus import EventBus
    from ayeon.runtime.supervisor import LIFECYCLE_TRANSITIONED

    bus = EventBus()
    events = []
    bus.subscribe(LIFECYCLE_TRANSITIONED, events.append)

    runtime = SupervisorRuntime(event_bus=bus)
    trace = TraceContext.root()

    runtime.transition_to(
        LifecycleState.BOOTING,
        reason="Startup requested.",
        initiated_by="runtime",
        trace=trace,
    )

    assert events[0].trace.correlation_id == trace.correlation_id


def test_rejected_transition_does_not_emit_lifecycle_event() -> None:
    from ayeon.runtime.event_bus import EventBus
    from ayeon.runtime.supervisor import LIFECYCLE_TRANSITIONED

    bus = EventBus()
    events = []
    bus.subscribe(LIFECYCLE_TRANSITIONED, events.append)

    runtime = SupervisorRuntime(event_bus=bus)

    with pytest.raises(InvalidLifecycleTransitionError):
        runtime.transition_to(
            LifecycleState.RUNNING,
            reason="Attempt to skip boot.",
            initiated_by="runtime",
            trace=TraceContext.root(),
        )

    assert events == []

def test_failing_lifecycle_observer_does_not_undo_transition() -> None:
    from ayeon.runtime.event_bus import (
        EVENT_HANDLER_FAILED,
        EventBus,
    )
    from ayeon.runtime.supervisor import LIFECYCLE_TRANSITIONED

    bus = EventBus()
    failure_events = []

    def failing_observer(event) -> None:
        raise RuntimeError("observer failed")

    bus.subscribe(LIFECYCLE_TRANSITIONED, failing_observer)
    bus.subscribe(EVENT_HANDLER_FAILED, failure_events.append)

    runtime = SupervisorRuntime(event_bus=bus)
    trace = TraceContext.root()

    transition = runtime.transition_to(
        LifecycleState.BOOTING,
        reason="Startup requested.",
        initiated_by="runtime",
        trace=trace,
    )

    assert transition.target is LifecycleState.BOOTING
    assert runtime.state is LifecycleState.BOOTING
    assert runtime.last_transition is transition

    assert len(failure_events) == 1
    assert failure_events[0].payload["error_type"] == "RuntimeError"
    assert failure_events[0].payload["error_message"] == "observer failed"


def test_state_view_reflects_current_runtime_state() -> None:
    runtime = SupervisorRuntime()

    view = runtime.state_view()

    assert view.lifecycle is LifecycleState.STOPPED
    assert view.health is HealthState.HEALTHY
    assert view.health_reports == ()
    assert view.has_critical_failure is False


def test_state_view_is_stable_after_runtime_changes() -> None:
    runtime = SupervisorRuntime()
    view = runtime.state_view()

    runtime.report_health(
        HealthReport(
            component="memory",
            state=HealthState.FAILED,
            criticality=ComponentCriticality.CRITICAL,
            reason="Memory subsystem failed.",
        )
    )

    assert view.health is HealthState.HEALTHY
    assert view.health_reports == ()
    assert view.has_critical_failure is False

    current = runtime.state_view()

    assert current.health is HealthState.FAILED
    assert len(current.health_reports) == 1
    assert current.has_critical_failure is True
