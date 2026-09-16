import pytest

from ayeon.contracts.capabilities import CapabilityState, CapabilityStatus


def test_available_capability_reports_available() -> None:
    capability = CapabilityStatus(
        capability="network.internet",
        state=CapabilityState.AVAILABLE,
        source="host_probe",
    )

    assert capability.is_available is True


def test_degraded_capability_is_not_fully_available() -> None:
    capability = CapabilityStatus(
        capability="gpu.compute",
        state=CapabilityState.DEGRADED,
        source="host_probe",
        reason="Reduced compute capacity.",
    )

    assert capability.is_available is False
    assert capability.state is CapabilityState.DEGRADED


def test_unauthorized_is_distinct_from_unavailable() -> None:
    unauthorized = CapabilityStatus(
        capability="camera",
        state=CapabilityState.UNAUTHORIZED,
        source="host_probe",
    )
    unavailable = CapabilityStatus(
        capability="camera",
        state=CapabilityState.UNAVAILABLE,
        source="host_probe",
    )

    assert unauthorized.state is not unavailable.state


def test_unknown_is_distinct_from_failed() -> None:
    unknown = CapabilityStatus(
        capability="microphone",
        state=CapabilityState.UNKNOWN,
        source="host_probe",
    )
    failed = CapabilityStatus(
        capability="microphone",
        state=CapabilityState.FAILED,
        source="host_probe",
    )

    assert unknown.state is not failed.state


def test_capability_contains_no_action_authorization() -> None:
    capability = CapabilityStatus(
        capability="email.send",
        state=CapabilityState.AVAILABLE,
        source="host_probe",
    )

    assert not hasattr(capability, "authorized")
    assert not hasattr(capability, "authorization")
    assert not hasattr(capability, "permission")


def test_empty_capability_name_is_rejected() -> None:
    with pytest.raises(ValueError, match="capability must not be empty"):
        CapabilityStatus(
            capability=" ",
            state=CapabilityState.AVAILABLE,
            source="host_probe",
        )


def test_empty_source_is_rejected() -> None:
    with pytest.raises(ValueError, match="source must not be empty"):
        CapabilityStatus(
            capability="network.internet",
            state=CapabilityState.AVAILABLE,
            source=" ",
        )


def test_blank_reason_is_rejected() -> None:
    with pytest.raises(ValueError, match="reason must not be blank"):
        CapabilityStatus(
            capability="network.internet",
            state=CapabilityState.FAILED,
            source="host_probe",
            reason=" ",
        )
