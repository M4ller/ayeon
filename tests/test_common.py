from datetime import UTC
from uuid import UUID

from ayeon.contracts.common import ResultState, TraceContext, utc_now


def test_utc_now_is_timezone_aware_and_utc() -> None:
    now = utc_now()

    assert now.tzinfo is UTC


def test_root_trace_has_valid_correlation_id() -> None:
    trace = TraceContext.root()

    assert isinstance(trace.correlation_id, UUID)
    assert trace.causation_id is None


def test_result_state_keeps_unknown_distinct_from_success() -> None:
    assert ResultState.UNKNOWN != ResultState.SUCCESS
    assert ResultState.UNKNOWN.value == "unknown"
    assert ResultState.SUCCESS.value == "success"


def test_new_memory_intent_id_returns_unique_ids() -> None:
    from ayeon.contracts.common import new_memory_intent_id

    first = new_memory_intent_id()
    second = new_memory_intent_id()

    assert first != second
