import pytest

from ayeon.contracts.lifecycle import LifecycleState
from ayeon.runtime.lifecycle_policy import LifecyclePolicy


@pytest.mark.parametrize(
    ("current", "target"),
    [
        (LifecycleState.STOPPED, LifecycleState.BOOTING),
        (LifecycleState.BOOTING, LifecycleState.VERIFYING),
        (LifecycleState.VERIFYING, LifecycleState.RUNNING),
        (LifecycleState.VERIFYING, LifecycleState.SAFE_MODE),
        (LifecycleState.RUNNING, LifecycleState.DEGRADED),
        (LifecycleState.DEGRADED, LifecycleState.RECOVERING),
        (LifecycleState.SAFE_MODE, LifecycleState.RECOVERING),
        (LifecycleState.RECOVERING, LifecycleState.VERIFYING),
        (LifecycleState.RUNNING, LifecycleState.SHUTTING_DOWN),
        (LifecycleState.SHUTTING_DOWN, LifecycleState.STOPPED),
    ],
)
def test_allowed_lifecycle_transitions(
    current: LifecycleState,
    target: LifecycleState,
) -> None:
    assert LifecyclePolicy.can_transition(current, target) is True


@pytest.mark.parametrize(
    ("current", "target"),
    [
        (LifecycleState.STOPPED, LifecycleState.RUNNING),
        (LifecycleState.BOOTING, LifecycleState.RUNNING),
        (LifecycleState.RECOVERING, LifecycleState.RUNNING),
        (LifecycleState.STOPPED, LifecycleState.STOPPED),
        (LifecycleState.RUNNING, LifecycleState.BOOTING),
        (LifecycleState.SAFE_MODE, LifecycleState.RUNNING),
    ],
)
def test_forbidden_lifecycle_transitions(
    current: LifecycleState,
    target: LifecycleState,
) -> None:
    assert LifecyclePolicy.can_transition(current, target) is False


def test_recovery_requires_verification_before_running() -> None:
    assert LifecyclePolicy.can_transition(
        LifecycleState.RECOVERING,
        LifecycleState.VERIFYING,
    )
    assert not LifecyclePolicy.can_transition(
        LifecycleState.RECOVERING,
        LifecycleState.RUNNING,
    )


def test_boot_cannot_skip_verification() -> None:
    assert LifecyclePolicy.can_transition(
        LifecycleState.BOOTING,
        LifecycleState.VERIFYING,
    )
    assert not LifecyclePolicy.can_transition(
        LifecycleState.BOOTING,
        LifecycleState.RUNNING,
    )
