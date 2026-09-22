"""Memory persistence result verification association contracts."""

from __future__ import annotations

from dataclasses import dataclass

from ayeon.contracts.memory_persistence import MemoryPersistenceResult
from ayeon.contracts.memory_persistence_verification import (
    MemoryPersistenceVerificationResult,
)


@dataclass(frozen=True, slots=True)
class MemoryPersistenceResultVerification:
    """Associate one persistence result with its verification evidence.

    This contract proves association consistency only.
    The persistence and verification states remain independent.
    """

    persistence: MemoryPersistenceResult
    verification: MemoryPersistenceVerificationResult

    def __post_init__(self) -> None:
        if (
            self.verification.memory_record_id
            != self.persistence.memory_record_id
        ):
            raise ValueError(
                "verification memory_record_id must match persistence "
                "memory_record_id"
            )

        if (
            self.verification.repository_name
            != self.persistence.repository_name
        ):
            raise ValueError(
                "verification repository_name must match persistence "
                "repository_name"
            )

        if (
            self.verification.trace.correlation_id
            != self.persistence.trace.correlation_id
        ):
            raise ValueError(
                "verification correlation_id must match persistence "
                "correlation_id"
            )