from datetime import datetime

import pytest

from ayeon.contracts.common import TraceContext
from ayeon.contracts.verification import VerificationResult, VerificationState


def test_verified_result_records_subject_and_trace() -> None:
    trace = TraceContext.root()

    result = VerificationResult(
        subject="identity",
        state=VerificationState.VERIFIED,
        verified_by="identity_verifier",
        trace=trace,
        reason="Identity integrity verified.",
    )

    assert result.subject == "identity"
    assert result.state is VerificationState.VERIFIED
    assert result.trace.correlation_id == trace.correlation_id
    assert result.checked_at.tzinfo is not None


def test_unknown_is_distinct_from_verified() -> None:
    assert VerificationState.UNKNOWN is not VerificationState.VERIFIED


def test_failed_is_distinct_from_verified() -> None:
    assert VerificationState.FAILED is not VerificationState.VERIFIED


def test_empty_subject_is_rejected() -> None:
    with pytest.raises(ValueError, match="subject must not be empty"):
        VerificationResult(
            subject=" ",
            state=VerificationState.VERIFIED,
            verified_by="identity_verifier",
            trace=TraceContext.root(),
            reason="Verification completed.",
        )


def test_empty_verifier_is_rejected() -> None:
    with pytest.raises(ValueError, match="verified_by must not be empty"):
        VerificationResult(
            subject="identity",
            state=VerificationState.VERIFIED,
            verified_by=" ",
            trace=TraceContext.root(),
            reason="Verification completed.",
        )


def test_empty_reason_is_rejected() -> None:
    with pytest.raises(ValueError, match="reason must not be empty"):
        VerificationResult(
            subject="identity",
            state=VerificationState.VERIFIED,
            verified_by="identity_verifier",
            trace=TraceContext.root(),
            reason=" ",
        )


def test_naive_verification_timestamp_is_rejected() -> None:
    with pytest.raises(ValueError, match="checked_at must be timezone-aware"):
        VerificationResult(
            subject="identity",
            state=VerificationState.VERIFIED,
            verified_by="identity_verifier",
            trace=TraceContext.root(),
            reason="Verification completed.",
            checked_at=datetime(2026, 1, 1),
        )
