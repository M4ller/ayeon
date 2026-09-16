from datetime import datetime

import pytest

from ayeon.contracts.action_verification import ActionVerificationResult
from ayeon.contracts.common import (
    TraceContext,
    new_action_id,
    new_attempt_id,
)
from ayeon.contracts.verification import VerificationState


def test_action_verification_result_preserves_attempt_identity() -> None:
    action_id = new_action_id()
    attempt_id = new_attempt_id()
    trace = TraceContext.root()

    result = ActionVerificationResult(
        action_id=action_id,
        attempt_id=attempt_id,
        state=VerificationState.VERIFIED,
        verified_by="fake_verifier",
        trace=trace,
        reason="Observed expected external effect.",
    )

    assert result.action_id == action_id
    assert result.attempt_id == attempt_id
    assert result.state is VerificationState.VERIFIED
    assert result.verified_by == "fake_verifier"
    assert result.trace is trace
    assert result.reason == "Observed expected external effect."
    assert result.checked_at.tzinfo is not None

def test_action_verification_rejects_blank_verified_by() -> None:
    with pytest.raises(ValueError, match="verified_by"):
        ActionVerificationResult(
            action_id=new_action_id(),
            attempt_id=new_attempt_id(),
            state=VerificationState.UNKNOWN,
            verified_by="   ",
            trace=TraceContext.root(),
            reason="Verification could not establish the effect.",
        )


def test_action_verification_rejects_blank_reason() -> None:
    with pytest.raises(ValueError, match="reason"):
        ActionVerificationResult(
            action_id=new_action_id(),
            attempt_id=new_attempt_id(),
            state=VerificationState.UNKNOWN,
            verified_by="fake_verifier",
            trace=TraceContext.root(),
            reason="   ",
        )


def test_action_verification_requires_timezone_aware_checked_at() -> None:
    with pytest.raises(ValueError, match="timezone-aware"):
        ActionVerificationResult(
            action_id=new_action_id(),
            attempt_id=new_attempt_id(),
            state=VerificationState.UNKNOWN,
            verified_by="fake_verifier",
            trace=TraceContext.root(),
            reason="Verification could not establish the effect.",
            checked_at=datetime(2026, 1, 1, 12, 0),
        )