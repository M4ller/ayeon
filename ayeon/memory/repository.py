"""Memory repository boundary for Ayeon Core."""

from __future__ import annotations

from typing import Protocol, runtime_checkable

from ayeon.contracts.memory import MemoryRecord
from ayeon.contracts.memory_persistence import MemoryPersistenceResult


@runtime_checkable
class MemoryRepository(Protocol):
    """Structural boundary for memory persistence implementations.

    A repository stores already materialized MemoryRecord objects.
    It does not decide memory admission or materialization eligibility.
    """

    @property
    def name(self) -> str:
        """Return the canonical repository name."""
        ...

    def store(
        self,
        record: MemoryRecord,
    ) -> MemoryPersistenceResult:
        """Attempt to persist one materialized memory record."""
        ...
