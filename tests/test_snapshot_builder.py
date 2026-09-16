from ayeon.contracts.common import HealthState
from ayeon.contracts.lifecycle import LifecycleState
from ayeon.contracts.runtime_state import RuntimeStateView
from ayeon.runtime.snapshot_builder import StateSnapshotBuilder


def test_builder_starts_snapshot_sequence_at_zero() -> None:
    builder = StateSnapshotBuilder()

    runtime = RuntimeStateView(
        lifecycle=LifecycleState.STOPPED,
        health=HealthState.HEALTHY,
        health_reports=(),
        has_critical_failure=False,
    )

    snapshot = builder.build(runtime=runtime)

    assert snapshot.sequence == 0
    assert snapshot.runtime_health is HealthState.HEALTHY
    assert snapshot.domain("runtime") is runtime


def test_builder_increments_snapshot_sequence() -> None:
    builder = StateSnapshotBuilder()

    runtime = RuntimeStateView(
        lifecycle=LifecycleState.STOPPED,
        health=HealthState.HEALTHY,
        health_reports=(),
        has_critical_failure=False,
    )

    first = builder.build(runtime=runtime)
    second = builder.build(runtime=runtime)

    assert first.sequence == 0
    assert second.sequence == 1

def test_previous_snapshot_remains_stable_after_next_build() -> None:
    builder = StateSnapshotBuilder()

    stopped = RuntimeStateView(
        lifecycle=LifecycleState.STOPPED,
        health=HealthState.HEALTHY,
        health_reports=(),
        has_critical_failure=False,
    )

    running = RuntimeStateView(
        lifecycle=LifecycleState.RUNNING,
        health=HealthState.DEGRADED,
        health_reports=(),
        has_critical_failure=False,
    )

    first = builder.build(runtime=stopped)
    second = builder.build(runtime=running)

    assert first.sequence == 0
    assert first.domain("runtime") is stopped
    assert first.runtime_health is HealthState.HEALTHY

    assert second.sequence == 1
    assert second.domain("runtime") is running
    assert second.runtime_health is HealthState.DEGRADED


def test_failed_build_does_not_consume_sequence() -> None:
    builder = StateSnapshotBuilder()

    import ayeon.runtime.snapshot_builder as snapshot_builder_module

    original_build = snapshot_builder_module.AyeonStateSnapshot

    class FailingSnapshot:
        def __init__(self, *args: object, **kwargs: object) -> None:
            raise ValueError("simulated snapshot failure")

    snapshot_builder_module.AyeonStateSnapshot = FailingSnapshot

    runtime = RuntimeStateView(
        lifecycle=LifecycleState.STOPPED,
        health=HealthState.HEALTHY,
        health_reports=(),
        has_critical_failure=False,
    )

    try:
        try:
            builder.build(runtime=runtime)
        except ValueError:
            pass
    finally:
        snapshot_builder_module.AyeonStateSnapshot = original_build

    snapshot = builder.build(runtime=runtime)

    assert snapshot.sequence == 0

def test_builder_integrates_with_supervisor_runtime_view() -> None:
    from ayeon.contracts.health import ComponentCriticality, HealthReport
    from ayeon.runtime.supervisor import SupervisorRuntime

    runtime = SupervisorRuntime()
    builder = StateSnapshotBuilder()

    runtime.report_health(
        HealthReport(
            component="memory",
            state=HealthState.DEGRADED,
            criticality=ComponentCriticality.IMPORTANT,
            reason="Memory subsystem degraded.",
        )
    )

    runtime_view = runtime.state_view()
    snapshot = builder.build(runtime=runtime_view)

    assert snapshot.sequence == 0
    assert snapshot.runtime_health is HealthState.DEGRADED
    assert snapshot.domain("runtime") is runtime_view
    assert snapshot.domain("runtime").lifecycle is LifecycleState.STOPPED
    assert len(snapshot.domain("runtime").health_reports) == 1