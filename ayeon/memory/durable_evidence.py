"""Durable memory evidence boundary for Ayeon Core."""

from __future__ import annotations

from typing import Protocol, runtime_checkable

from ayeon.contracts.common import MemoryRecordId


@runtime_checkable
class DurableMemoryEvidenceReader(Protocol):
    """Read canonical durable evidence without semantic memory retrieval."""

    @property
    def name(self) -> str:
        """Return the canonical evidence reader name."""
        ...

    def read_payload(
        self,
        memory_record_id: MemoryRecordId,
    ) -> bytes | None:
        """Return durable payload bytes, or None for confirmed absence."""
        ...