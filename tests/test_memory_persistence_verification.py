from datetime import datetime

import pytest

from ayeon.contracts.common import TraceContext, new_memory_record_id
from ayeon.contracts.memory_persistence_verification import (
    MemoryPersistenceVerificationResult,
)
from ayeon.contracts.verification import VerificationState


def test_memory_persistence_verification_preserves_evidence() -> None:
    memory_record_id = new_memory_record_id()
    trace = TraceContext.root()

    result = MemoryPersistenceVerificationResult(
        memory_record_id=memory_record_id,
        repository_name="test_repository",
        state=VerificationState.VERIFIED,
        verified_by="test_verifier",
        trace=trace,
        reason="Observed expected durable memory record.",
    )

    assert result.memory_record_id == memory_record_id
    assert result.repository_name == "test_repository"
    assert result.state is VerificationState.VERIFIED
    assert result.verified_by == "test_verifier"
    assert result.trace is trace
    assert result.reason == "Observed expected durable memory record."
    assert isinstance(result.checked_at, datetime)
    assert result.checked_at.tzinfo is not None


@pytest.mark.parametrize(
    ("field_name", "value", "expected_message"),
    [
        ("repository_name", "   ", "repository_name must not be empty"),
        ("verified_by", "   ", "verified_by must not be empty"),
        ("reason", "   ", "reason must not be empty"),
    ],
)
def test_memory_persistence_verification_rejects_blank_text_fields(
    field_name: str,
    value: str,
    expected_message: str,
) -> None:
    kwargs = {
        "memory_record_id": new_memory_record_id(),
        "repository_name": "test_repository",
        "state": VerificationState.UNKNOWN,
        "verified_by": "test_verifier",
        "trace": TraceContext.root(),
        "reason": "Verification could not establish durable state.",
    }
    kwargs[field_name] = value

    with pytest.raises(ValueError, match=expected_message):
        MemoryPersistenceVerificationResult(**kwargs)


def test_memory_persistence_verification_rejects_invalid_state() -> None:
    with pytest.raises(TypeError, match="state must be VerificationState"):
        MemoryPersistenceVerificationResult(
            memory_record_id=new_memory_record_id(),
            repository_name="test_repository",
            state="verified",
            verified_by="test_verifier",
            trace=TraceContext.root(),
            reason="Observed expected durable memory record.",
        )


def test_memory_persistence_verification_requires_timezone_aware_checked_at(
) -> None:
    with pytest.raises(ValueError, match="timezone-aware"):
        MemoryPersistenceVerificationResult(
            memory_record_id=new_memory_record_id(),
            repository_name="test_repository",
            state=VerificationState.UNKNOWN,
            verified_by="test_verifier",
            trace=TraceContext.root(),
            reason="Verification could not establish durable state.",
            checked_at=datetime(2026, 1, 1, 12, 0),
        )