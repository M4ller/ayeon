"""Separate local reference for expected durable memory records."""

from __future__ import annotations

import os
from pathlib import Path

from ayeon.contracts.common import TraceContext
from ayeon.contracts.memory import (
    AdmittedMemoryIntent,
    MemoryAdmissionDecision,
    MemoryAdmissionOutcome,
    MemoryIntent,
    MemoryRecord,
)
from ayeon.memory.decoder import decode_memory_record
from ayeon.memory.serialization import encode_memory_record


class LocalMemoryReferenceStore:
    """Keep canonical expected records separately from the SQLite database."""

    def __init__(self, path: str | Path) -> None:
        self._path = Path(path)

    def append(self, record: MemoryRecord) -> None:
        self._path.parent.mkdir(parents=True, exist_ok=True)
        with self._path.open("ab") as stream:
            stream.write(encode_memory_record(record) + b"\n")
            stream.flush()
            os.fsync(stream.fileno())

    def remove(self, record: MemoryRecord) -> bool:
        """Remove only an exact canonical reference."""
        if not self._path.exists():
            return False

        lines = self._path.read_bytes().splitlines(keepends=True)
        expected = encode_memory_record(record) + b"\n"
        if any(not line.endswith(b"\n") for line in lines):
            return False
        if lines.count(expected) != 1:
            return False

        temporary = self._path.with_name(self._path.name + ".tmp")
        with temporary.open("wb") as stream:
            stream.write(b"".join(line for line in lines if line != expected))
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, self._path)
        return True

    def load(self) -> list[MemoryRecord]:
        if not self._path.exists():
            return []

        records = []
        seen = set()
        for line in self._path.read_bytes().splitlines(keepends=True):
            if not line.endswith(b"\n"):
                continue
            try:
                decoded = decode_memory_record(line[:-1])
                trace = TraceContext(
                    correlation_id=decoded.correlation_id,
                    causation_id=decoded.causation_id,
                )
                intent = MemoryIntent(
                    content=decoded.content,
                    proposed_by="console_demo",
                    trace=trace,
                    reason="Restored local reference.",
                    memory_intent_id=decoded.source_memory_intent_id,
                )
                admission = MemoryAdmissionDecision(
                    memory_intent_id=intent.memory_intent_id,
                    outcome=MemoryAdmissionOutcome.ACCEPT,
                    decided_by="console_demo",
                    trace=trace,
                    reason="Restored admitted reference.",
                )
                record = MemoryRecord(
                    admitted=AdmittedMemoryIntent(intent=intent, admission=admission),
                    memory_record_id=decoded.memory_record_id,
                    created_at=decoded.created_at,
                )
                if encode_memory_record(record) != line[:-1]:
                    continue
                if record.memory_record_id not in seen:
                    records.append(record)
                    seen.add(record.memory_record_id)
            except (TypeError, ValueError):
                continue
        return records
