from datetime import datetime

import pytest

from ayeon.contracts.common import TraceContext
from ayeon.contracts.memory import MemoryIntent


def test_memory_intent_preserves_proposal_identity_and_trace() -> None:
    trace = TraceContext.root()

    intent = MemoryIntent(
        content={"kind": "observation", "text": "Felipe prefers concise output."},
        proposed_by="cognition",
        trace=trace,
    )

    assert intent.trace is trace
    assert intent.proposed_by == "cognition"
    assert intent.memory_intent_id is not None


def test_memory_intent_rejects_empty_content() -> None:
    with pytest.raises(ValueError, match="content must not be empty"):
        MemoryIntent(
            content={},
            proposed_by="cognition",
            trace=TraceContext.root(),
        )


def test_memory_intent_rejects_empty_proposed_by() -> None:
    with pytest.raises(ValueError, match="proposed_by must not be empty"):
        MemoryIntent(
            content={"kind": "observation"},
            proposed_by=" ",
            trace=TraceContext.root(),
        )


def test_memory_intent_rejects_naive_timestamp() -> None:
    with pytest.raises(ValueError, match="created_at must be timezone-aware"):
        MemoryIntent(
            content={"kind": "observation"},
            proposed_by="cognition",
            trace=TraceContext.root(),
            created_at=datetime(2026, 1, 1),
        )


def test_memory_intent_copies_mutable_content() -> None:
    content = {"kind": "observation"}

    intent = MemoryIntent(
        content=content,
        proposed_by="cognition",
        trace=TraceContext.root(),
    )

    content["kind"] = "changed"

    assert intent.content["kind"] == "observation"


def test_memory_intent_content_is_read_only() -> None:
    intent = MemoryIntent(
        content={"kind": "observation"},
        proposed_by="cognition",
        trace=TraceContext.root(),
    )

    with pytest.raises(TypeError):
        intent.content["kind"] = "changed"
