"""State snapshot contracts for Ayeon Core."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field
from datetime import datetime
from types import MappingProxyType

from ayeon.contracts.common import HealthState, utc_now
from ayeon.contracts.runtime_state import RuntimeStateView


@dataclass(frozen=True, slots=True)
class AyeonStateSnapshot:
    """Immutable read-only view of Ayeon's distributed state.

    A snapshot is a coherent observation of authoritative domain states.
    It is not an owner of those states and must not be used to mutate them.
    """

    sequence: int
    runtime_health: HealthState
    domains: Mapping[str, object] = field(default_factory=dict)
    captured_at: datetime = field(default_factory=utc_now)

    def __post_init__(self) -> None:
        if self.sequence < 0:
            raise ValueError("sequence must not be negative")

        if self.captured_at.tzinfo is None:
            raise ValueError("captured_at must be timezone-aware")

        runtime = self.domains.get("runtime")

        if isinstance(runtime, RuntimeStateView):
            if runtime.health is not self.runtime_health:
                raise ValueError(
                    "runtime_health must match runtime domain health"
                )

        safe_domains = MappingProxyType(dict(self.domains))
        object.__setattr__(self, "domains", safe_domains)

    def domain(self, name: str) -> object | None:
        """Return a domain snapshot without exposing mutable ownership."""

        return self.domains.get(name)
