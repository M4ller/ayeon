from datetime import datetime

import pytest

from ayeon.contracts.common import HealthState
from ayeon.contracts.health import HealthReport
from ayeon.runtime.health import RuntimeHealth


def test_runtime_health_starts_healthy() -> None:
    health = RuntimeHealth()

    assert health.overall is HealthState.HEALTHY


def test_health_report_is_stored_by_component() -> None:
    health = RuntimeHealth()
    report = HealthReport(
        component="memory",
        state=HealthState.HEALTHY,
    )

    health.report(report)

    assert health.get("memory") is report


def test_latest_report_replaces_previous_component_report() -> None:
    health = RuntimeHealth()

    health.report(
        HealthReport(
            component="memory",
            state=HealthState.DEGRADED,
            reason="Slow response.",
        )
    )
    latest = HealthReport(
        component="memory",
        state=HealthState.HEALTHY,
        reason="Recovered.",
    )
    health.report(latest)

    assert health.get("memory") is latest
    assert health.overall is HealthState.HEALTHY


def test_degraded_component_degrades_overall_health() -> None:
    health = RuntimeHealth()

    health.report(
        HealthReport(
            component="memory",
            state=HealthState.HEALTHY,
        )
    )
    health.report(
        HealthReport(
            component="perception",
            state=HealthState.DEGRADED,
            reason="Camera unavailable.",
        )
    )

    assert health.overall is HealthState.DEGRADED


def test_failed_component_has_highest_severity() -> None:
    health = RuntimeHealth()

    health.report(
        HealthReport(
            component="memory",
            state=HealthState.DEGRADED,
            reason="Slow response.",
        )
    )
    health.report(
        HealthReport(
            component="identity",
            state=HealthState.FAILED,
            reason="Integrity verification failed.",
        )
    )

    assert health.overall is HealthState.FAILED


def test_empty_component_is_rejected() -> None:
    with pytest.raises(ValueError, match="component must not be empty"):
        HealthReport(
            component=" ",
            state=HealthState.HEALTHY,
        )


def test_blank_reason_is_rejected() -> None:
    with pytest.raises(ValueError, match="reason must not be blank"):
        HealthReport(
            component="memory",
            state=HealthState.DEGRADED,
            reason=" ",
        )


def test_naive_health_timestamp_is_rejected() -> None:
    with pytest.raises(ValueError, match="checked_at must be timezone-aware"):
        HealthReport(
            component="memory",
            state=HealthState.HEALTHY,
            checked_at=datetime(2026, 1, 1),
        )

def test_optional_failure_is_not_critical_failure() -> None:
    from ayeon.contracts.health import ComponentCriticality

    health = RuntimeHealth()
    health.report(
        HealthReport(
            component="camera",
            state=HealthState.FAILED,
            criticality=ComponentCriticality.OPTIONAL,
            reason="Camera disconnected.",
        )
    )

    assert health.overall is HealthState.FAILED
    assert health.has_critical_failure is False


def test_critical_failure_is_detected() -> None:
    from ayeon.contracts.health import ComponentCriticality

    health = RuntimeHealth()
    health.report(
        HealthReport(
            component="identity",
            state=HealthState.FAILED,
            criticality=ComponentCriticality.CRITICAL,
            reason="Identity integrity verification failed.",
        )
    )

    assert health.has_critical_failure is True


def test_recovered_critical_component_clears_critical_failure() -> None:
    from ayeon.contracts.health import ComponentCriticality

    health = RuntimeHealth()

    health.report(
        HealthReport(
            component="continuity",
            state=HealthState.FAILED,
            criticality=ComponentCriticality.CRITICAL,
            reason="Continuity verification failed.",
        )
    )

    assert health.has_critical_failure is True

    health.report(
        HealthReport(
            component="continuity",
            state=HealthState.HEALTHY,
            criticality=ComponentCriticality.CRITICAL,
            reason="Continuity verified.",
        )
    )

    assert health.has_critical_failure is False

def test_reports_returns_immutable_snapshot() -> None:
    health = RuntimeHealth()

    report = HealthReport(
        component="memory",
        state=HealthState.HEALTHY,
        reason="Memory subsystem healthy.",
    )

    health.report(report)

    reports = health.reports

    assert reports == (report,)
    assert isinstance(reports, tuple)


def test_reports_snapshot_does_not_change_after_new_report() -> None:
    health = RuntimeHealth()

    first = HealthReport(
        component="memory",
        state=HealthState.HEALTHY,
        reason="Memory subsystem healthy.",
    )

    health.report(first)
    snapshot = health.reports

    second = HealthReport(
        component="identity",
        state=HealthState.HEALTHY,
        reason="Identity subsystem healthy.",
    )

    health.report(second)

    assert snapshot == (first,)
    assert health.reports == (first, second)
