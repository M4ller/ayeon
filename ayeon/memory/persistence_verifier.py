"""Memory persistence verification boundary for Ayeon Core."""

from __future__ import annotations

from typing import Protocol, runtime_checkable

from ayeon.contracts.memory import MemoryRecord
from ayeon.contracts.memory_persistence import MemoryPersistenceResult
from ayeon.contracts.memory_persistence_verification import (
    MemoryPersistenceVerificationResult,
)


@runtime_checkable
class MemoryPersistenceVerifier(Protocol):
    """Structural boundary for independent memory persistence verification."""

    @property
    def name(self) -> str:
        """Return the canonical verifier name."""
        ...

    def verify(
        self,
        record: MemoryRecord,
        persistence: MemoryPersistenceResult,
    ) -> MemoryPersistenceVerificationResult:
        """Verify durable evidence against the expected memory record."""
        ...