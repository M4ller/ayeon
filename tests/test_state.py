from dataclasses import FrozenInstanceError
from datetime import datetime

import pytest

from ayeon.contracts.common import HealthState
from ayeon.contracts.state import AyeonStateSnapshot


def test_snapshot_exposes_domain_state() -> None:
    snapshot = AyeonStateSnapshot(
        sequence=1,
        runtime_health=HealthState.HEALTHY,
        domains={"identity": {"status": "verified"}},
    )

    assert snapshot.domain("identity") == {"status": "verified"}
    assert snapshot.domain("missing") is None


def test_snapshot_top_level_is_immutable() -> None:
    snapshot = AyeonStateSnapshot(
        sequence=1,
        runtime_health=HealthState.HEALTHY,
    )

    with pytest.raises(FrozenInstanceError):
        snapshot.sequence = 2


def test_snapshot_domains_mapping_is_read_only() -> None:
    snapshot = AyeonStateSnapshot(
        sequence=1,
        runtime_health=HealthState.HEALTHY,
        domains={"runtime": "running"},
    )

    with pytest.raises(TypeError):
        snapshot.domains["runtime"] = "failed"


def test_snapshot_defensively_copies_domains() -> None:
    original = {"runtime": "running"}

    snapshot = AyeonStateSnapshot(
        sequence=1,
        runtime_health=HealthState.HEALTHY,
        domains=original,
    )

    original["runtime"] = "failed"

    assert snapshot.domain("runtime") == "running"


def test_negative_sequence_is_rejected() -> None:
    with pytest.raises(ValueError, match="sequence must not be negative"):
        AyeonStateSnapshot(
            sequence=-1,
            runtime_health=HealthState.HEALTHY,
        )


def test_snapshot_timestamp_is_timezone_aware() -> None:
    snapshot = AyeonStateSnapshot(
        sequence=1,
        runtime_health=HealthState.HEALTHY,
    )

    assert snapshot.captured_at.tzinfo is not None


def test_naive_snapshot_timestamp_is_rejected() -> None:
    with pytest.raises(ValueError, match="captured_at must be timezone-aware"):
        AyeonStateSnapshot(
            sequence=1,
            runtime_health=HealthState.HEALTHY,
            captured_at=datetime(2026, 1, 1),
        )


def test_snapshot_can_expose_typed_runtime_domain() -> None:
    from ayeon.contracts.lifecycle import LifecycleState
    from ayeon.contracts.runtime_state import RuntimeStateView

    runtime = RuntimeStateView(
        lifecycle=LifecycleState.RUNNING,
        health=HealthState.HEALTHY,
        health_reports=(),
        has_critical_failure=False,
    )

    snapshot = AyeonStateSnapshot(
        sequence=1,
        runtime_health=HealthState.HEALTHY,
        domains={"runtime": runtime},
    )

    assert snapshot.domain("runtime") is runtime


def test_snapshot_rejects_runtime_health_mismatch() -> None:
    import pytest

    from ayeon.contracts.lifecycle import LifecycleState
    from ayeon.contracts.runtime_state import RuntimeStateView

    runtime = RuntimeStateView(
        lifecycle=LifecycleState.DEGRADED,
        health=HealthState.DEGRADED,
        health_reports=(),
        has_critical_failure=False,
    )

    with pytest.raises(ValueError, match="runtime_health"):
        AyeonStateSnapshot(
            sequence=1,
            runtime_health=HealthState.HEALTHY,
            domains={"runtime": runtime},
        )