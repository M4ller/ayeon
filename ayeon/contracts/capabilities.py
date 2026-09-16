"""Capability contracts for Ayeon Core."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


class CapabilityState(StrEnum):
    """Operational availability of a host capability."""

    AVAILABLE = "available"
    UNAVAILABLE = "unavailable"
    DISABLED = "disabled"
    UNAUTHORIZED = "unauthorized"
    DEGRADED = "degraded"
    FAILED = "failed"
    INCOMPATIBLE = "incompatible"
    UNKNOWN = "unknown"


@dataclass(frozen=True, slots=True)
class CapabilityStatus:
    """Observed operational state of one capability.

    Availability describes what the environment can currently provide.
    It does not grant authorization to use that capability.
    """

    capability: str
    state: CapabilityState
    source: str
    reason: str | None = None

    def __post_init__(self) -> None:
        if not self.capability.strip():
            raise ValueError("capability must not be empty")

        if not self.source.strip():
            raise ValueError("source must not be empty")

        if self.reason is not None and not self.reason.strip():
            raise ValueError("reason must not be blank")

    @property
    def is_available(self) -> bool:
        """Return whether the capability is operationally available."""

        return self.state is CapabilityState.AVAILABLE
