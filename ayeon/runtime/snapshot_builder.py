"""State snapshot builder for Ayeon Core."""

from __future__ import annotations

from ayeon.contracts.runtime_state import RuntimeStateView
from ayeon.contracts.state import AyeonStateSnapshot


class StateSnapshotBuilder:
    """Build coherent global state snapshots with monotonic sequencing."""

    def __init__(self) -> None:
        self._next_sequence = 0

    def build(
        self,
        *,
        runtime: RuntimeStateView,
    ) -> AyeonStateSnapshot:
        """Build the next immutable state snapshot."""

        snapshot = AyeonStateSnapshot(
            sequence=self._next_sequence,
            runtime_health=runtime.health,
            domains={"runtime": runtime},
        )

        self._next_sequence += 1
        return snapshot