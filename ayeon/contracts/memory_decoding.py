"""Contracts for decoded durable memory evidence."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from datetime import datetime
from types import MappingProxyType

from ayeon.contracts.common import (
    CausationId,
    CorrelationId,
    MemoryIntentId,
    MemoryRecordId,
)


@dataclass(frozen=True, slots=True)
class DecodedMemoryRecord:
    """Typed representation of fields present in durable memory payload.

    Decoding does not reconstruct a MemoryRecord and does not imply
    verification, relevance, or context inclusion.
    """

    memory_record_id: MemoryRecordId
    source_memory_intent_id: MemoryIntentId
    created_at: datetime
    correlation_id: CorrelationId
    causation_id: CausationId | None
    content: Mapping[str, object]

    def __post_init__(self) -> None:
        if self.created_at.tzinfo is None:
            raise ValueError("created_at must be timezone-aware")

        if not self.content:
            raise ValueError("content must not be empty")

        object.__setattr__(
            self,
            "content",
            MappingProxyType(dict(self.content)),
        )