from dataclasses import FrozenInstanceError

import pytest

from ayeon.contracts.approval import ApprovalEvidence
from ayeon.contracts.common import TraceContext, new_action_id


def test_approval_evidence_preserves_action_and_authority() -> None:
    trace = TraceContext.root()
    action_id = new_action_id()

    approval = ApprovalEvidence(
        action_id=action_id,
        approved_by="felipe",
        trace=trace,
        reason="Explicitly approved.",
    )

    assert approval.action_id == action_id
    assert approval.approved_by == "felipe"
    assert approval.trace == trace


def test_approval_evidence_is_immutable() -> None:
    approval = ApprovalEvidence(
        action_id=new_action_id(),
        approved_by="felipe",
        trace=TraceContext.root(),
        reason="Explicitly approved.",
    )

    with pytest.raises(FrozenInstanceError):
        approval.approved_by = "someone_else"


def test_approval_evidence_rejects_blank_authority() -> None:
    with pytest.raises(ValueError, match="approved_by"):
        ApprovalEvidence(
            action_id=new_action_id(),
            approved_by=" ",
            trace=TraceContext.root(),
            reason="Explicitly approved.",
        )


def test_approval_evidence_rejects_blank_reason() -> None:
    with pytest.raises(ValueError, match="reason"):
        ApprovalEvidence(
            action_id=new_action_id(),
            approved_by="felipe",
            trace=TraceContext.root(),
            reason=" ",
        )