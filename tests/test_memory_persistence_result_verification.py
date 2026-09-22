import pytest

from ayeon.contracts.common import (
    ResultState,
    TraceContext,
    new_memory_record_id,
)
from ayeon.contracts.memory_persistence import MemoryPersistenceResult
from ayeon.contracts.memory_persistence_result_verification import (
    MemoryPersistenceResultVerification,
)
from ayeon.contracts.memory_persistence_verification import (
    MemoryPersistenceVerificationResult,
)
from ayeon.contracts.verification import VerificationState


def make_persistence_result() -> MemoryPersistenceResult:
    return MemoryPersistenceResult(
        memory_record_id=new_memory_record_id(),
        repository_name="test_repository",
        state=ResultState.SUCCESS,
        trace=TraceContext.root(),
        summary="Stored.",
    )


def make_verification(
    persistence: MemoryPersistenceResult,
) -> MemoryPersistenceVerificationResult:
    return MemoryPersistenceVerificationResult(
        memory_record_id=persistence.memory_record_id,
        repository_name=persistence.repository_name,
        state=VerificationState.VERIFIED,
        verified_by="test_verifier",
        trace=persistence.trace,
        reason="Observed expected durable memory record.",
    )


def test_association_accepts_matching_persistence_and_verification() -> None:
    persistence = make_persistence_result()
    verification = make_verification(persistence)

    associated = MemoryPersistenceResultVerification(
        persistence=persistence,
        verification=verification,
    )

    assert associated.persistence is persistence
    assert associated.verification is verification


@pytest.mark.parametrize(
    "mismatch",
    ["memory_record_id", "repository_name", "correlation_id"],
)
def test_association_rejects_mismatched_verification(
    mismatch: str,
) -> None:
    persistence = make_persistence_result()

    memory_record_id = persistence.memory_record_id
    repository_name = persistence.repository_name
    trace = persistence.trace

    if mismatch == "memory_record_id":
        memory_record_id = new_memory_record_id()
    elif mismatch == "repository_name":
        repository_name = "different_repository"
    elif mismatch == "correlation_id":
        trace = TraceContext.root()

    verification = MemoryPersistenceVerificationResult(
        memory_record_id=memory_record_id,
        repository_name=repository_name,
        state=VerificationState.UNKNOWN,
        verified_by="test_verifier",
        trace=trace,
        reason="Verification evidence for association test.",
    )

    with pytest.raises(ValueError, match=mismatch):
        MemoryPersistenceResultVerification(
            persistence=persistence,
            verification=verification,
        )