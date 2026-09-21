import json
from datetime import timedelta

from ayeon.contracts.common import TraceContext
from ayeon.contracts.memory import (
    AdmittedMemoryIntent,
    MemoryAdmissionDecision,
    MemoryAdmissionOutcome,
    MemoryIntent,
    MemoryRecord,
)
from ayeon.memory.serialization import encode_memory_record


def make_record() -> MemoryRecord:
    trace = TraceContext.root()
    intent = MemoryIntent(
        content={"fact": "portable-first", "priority": 1},
        proposed_by="cognition",
        trace=trace,
        reason="Relevant architectural fact.",
    )
    admission = MemoryAdmissionDecision(
        memory_intent_id=intent.memory_intent_id,
        outcome=MemoryAdmissionOutcome.ACCEPT,
        decided_by="memory_intake_policy",
        trace=trace,
        reason="Accepted for durable memory.",
    )
    return MemoryRecord.from_admitted(
        AdmittedMemoryIntent(
            intent=intent,
            admission=admission,
        )
    )


def test_encode_memory_record_preserves_durable_identity_and_provenance() -> None:
    record = make_record()

    encoded = encode_memory_record(record)
    payload = json.loads(encoded.decode("utf-8"))

    assert payload["memory_record_id"] == str(record.memory_record_id)
    assert payload["source_memory_intent_id"] == str(
        record.source_memory_intent_id
    )
    assert payload["created_at"] == record.created_at.isoformat()
    assert payload["correlation_id"] == str(record.trace.correlation_id)
    assert payload["causation_id"] is None
    assert payload["content"] == dict(record.content)


def test_encode_memory_record_is_deterministic() -> None:
    record = make_record()

    assert encode_memory_record(record) == encode_memory_record(record)

def test_encode_memory_record_changes_when_durable_evidence_changes() -> None:
    original = make_record()
    conflicting = MemoryRecord(
        admitted=original.admitted,
        memory_record_id=original.memory_record_id,
        created_at=original.created_at + timedelta(seconds=1),
    )

    assert conflicting.memory_record_id == original.memory_record_id
    assert encode_memory_record(conflicting) != encode_memory_record(original)
