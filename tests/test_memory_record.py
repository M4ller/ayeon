from datetime import datetime

import pytest

from ayeon.contracts.common import TraceContext
from ayeon.contracts.memory import (
    AdmittedMemoryIntent,
    MemoryAdmissionDecision,
    MemoryAdmissionOutcome,
    MemoryIntent,
    MemoryRecord,
)


def make_admitted() -> AdmittedMemoryIntent:
    trace = TraceContext.root()
    intent = MemoryIntent(
        content={"fact": "portable-first"},
        proposed_by="cognition",
        trace=trace,
    )
    decision = MemoryAdmissionDecision(
        memory_intent_id=intent.memory_intent_id,
        outcome=MemoryAdmissionOutcome.ACCEPT,
        decided_by="memory_intake_policy",
        trace=trace,
        reason="test admission",
    )
    return AdmittedMemoryIntent(
        intent=intent,
        admission=decision,
    )


def test_memory_record_materializes_admitted_intent() -> None:
    admitted = make_admitted()

    record = MemoryRecord.from_admitted(admitted)

    assert record.source_memory_intent_id == admitted.intent.memory_intent_id
    assert record.trace is admitted.intent.trace
    assert dict(record.content) == dict(admitted.intent.content)
    assert record.memory_record_id != admitted.intent.memory_intent_id
    assert record.created_at.tzinfo is not None


def test_memory_record_content_is_defensively_copied() -> None:
    admitted = make_admitted()

    record = MemoryRecord.from_admitted(admitted)

    with pytest.raises(TypeError):
        record.content["fact"] = "mutated"


def test_memory_record_rejects_invalid_admitted_type() -> None:
    with pytest.raises(
        TypeError,
        match="admitted must be AdmittedMemoryIntent",
    ):
        MemoryRecord.from_admitted({"intent": "fake"})


def test_memory_record_created_at_is_datetime() -> None:
    admitted = make_admitted()

    record = MemoryRecord.from_admitted(admitted)

    assert isinstance(record.created_at, datetime)


def test_memory_record_preserves_admission_evidence() -> None:
    admitted = make_admitted()

    record = MemoryRecord.from_admitted(admitted)

    assert record.admitted is admitted
    assert record.admitted.intent is admitted.intent
    assert record.admitted.admission is admitted.admission
