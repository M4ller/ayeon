"""Memory entry approved for inclusion in cognitive context."""

from __future__ import annotations

from dataclasses import dataclass

from ayeon.contracts.common import MemoryRecordId
from ayeon.contracts.memory_decoding import DecodedMemoryRecord


@dataclass(frozen=True, slots=True)
class MemoryContextEntry:
    """Verified memory content selected for cognitive context."""

    memory_record_id: MemoryRecordId
    decoded: DecodedMemoryRecord

    def __post_init__(self) -> None:
        if self.decoded.memory_record_id != self.memory_record_id:
            raise ValueError(
                "decoded memory_record_id must match memory_record_id"
            )