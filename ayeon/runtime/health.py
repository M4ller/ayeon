"""Runtime health state owner for Ayeon Core."""

from __future__ import annotations

from ayeon.contracts.common import HealthState
from ayeon.contracts.health import ComponentCriticality, HealthReport


class RuntimeHealth:
    """Owns the current health reports for runtime components."""

    def __init__(self) -> None:
        self._reports: dict[str, HealthReport] = {}

    def report(self, health_report: HealthReport) -> None:
        """Record the latest health report for a component."""

        self._reports[health_report.component] = health_report

    def get(self, component: str) -> HealthReport | None:
        """Return the latest report for one component."""

        return self._reports.get(component)

    @property
    def overall(self) -> HealthState:
        """Return the most severe current runtime health state."""

        if not self._reports:
            return HealthState.HEALTHY

        states = {report.state for report in self._reports.values()}

        if HealthState.FAILED in states:
            return HealthState.FAILED

        if HealthState.DEGRADED in states:
            return HealthState.DEGRADED

        if HealthState.RECOVERING in states:
            return HealthState.RECOVERING

        if HealthState.UNAVAILABLE in states:
            return HealthState.UNAVAILABLE

        return HealthState.HEALTHY

    @property
    def has_critical_failure(self) -> bool:
        """Return whether any critical component is currently failed."""

        return any(
            report.criticality is ComponentCriticality.CRITICAL
            and report.state is HealthState.FAILED
            for report in self._reports.values()
        )

    @property
    def reports(self) -> tuple[HealthReport, ...]:
        """Return an immutable snapshot of current component health reports."""

        return tuple(self._reports.values())
