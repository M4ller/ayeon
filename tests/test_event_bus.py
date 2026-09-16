from ayeon.contracts.common import TraceContext
from ayeon.contracts.events import AyeonEvent, EventPersistence
from ayeon.runtime.event_bus import EventBus


def make_event(event_type: str = "runtime.test") -> AyeonEvent:
    return AyeonEvent(
        event_type=event_type,
        source="test",
        trace=TraceContext.root(),
        persistence=EventPersistence.EPHEMERAL,
        payload={"value": 42},
    )


def test_publish_delivers_event_to_subscriber() -> None:
    bus = EventBus()
    received: list[AyeonEvent] = []

    bus.subscribe("runtime.test", received.append)

    event = make_event()
    bus.publish(event)

    assert received == [event]


def test_publish_only_delivers_matching_event_type() -> None:
    bus = EventBus()
    received: list[AyeonEvent] = []

    bus.subscribe("runtime.expected", received.append)

    bus.publish(make_event("runtime.other"))

    assert received == []


def test_duplicate_subscription_does_not_duplicate_delivery() -> None:
    bus = EventBus()
    received: list[AyeonEvent] = []

    bus.subscribe("runtime.test", received.append)
    bus.subscribe("runtime.test", received.append)

    event = make_event()
    bus.publish(event)

    assert received == [event]


def test_unsubscribe_stops_delivery() -> None:
    bus = EventBus()
    received: list[AyeonEvent] = []

    bus.subscribe("runtime.test", received.append)
    bus.unsubscribe("runtime.test", received.append)

    bus.publish(make_event())

    assert received == []


def test_unsubscribe_unknown_handler_is_safe() -> None:
    bus = EventBus()

    def handler(event: AyeonEvent) -> None:
        pass

    bus.unsubscribe("runtime.test", handler)


def test_blank_event_type_is_rejected() -> None:
    bus = EventBus()

    def handler(event: AyeonEvent) -> None:
        pass

    try:
        bus.subscribe(" ", handler)
    except ValueError as error:
        assert str(error) == "event_type must not be empty"
    else:
        raise AssertionError("blank event_type should be rejected")


def test_subscriber_snapshot_allows_unsubscribe_during_publish() -> None:
    bus = EventBus()
    received: list[str] = []

    def first(event: AyeonEvent) -> None:
        received.append("first")
        bus.unsubscribe("runtime.test", second)

    def second(event: AyeonEvent) -> None:
        received.append("second")

    bus.subscribe("runtime.test", first)
    bus.subscribe("runtime.test", second)

    bus.publish(make_event())

    assert received == ["first", "second"]

    received.clear()
    bus.publish(make_event())

    assert received == ["first"]

def test_publish_result_reports_successful_delivery() -> None:
    bus = EventBus()
    received: list[AyeonEvent] = []

    bus.subscribe("runtime.test", received.append)

    result = bus.publish(make_event())

    assert result.delivered == 1
    assert result.failures == ()
    assert result.succeeded is True


def test_failing_handler_does_not_block_other_handlers() -> None:
    bus = EventBus()
    received: list[str] = []

    def first(event: AyeonEvent) -> None:
        received.append("first")

    def failing(event: AyeonEvent) -> None:
        received.append("failing")
        raise RuntimeError("handler failed")

    def third(event: AyeonEvent) -> None:
        received.append("third")

    bus.subscribe("runtime.test", first)
    bus.subscribe("runtime.test", failing)
    bus.subscribe("runtime.test", third)

    result = bus.publish(make_event())

    assert received == ["first", "failing", "third"]
    assert result.delivered == 2
    assert len(result.failures) == 1
    assert result.succeeded is False


def test_publish_result_preserves_handler_failure() -> None:
    bus = EventBus()

    def failing(event: AyeonEvent) -> None:
        raise RuntimeError("boom")

    bus.subscribe("runtime.test", failing)

    result = bus.publish(make_event())

    assert result.delivered == 0
    assert len(result.failures) == 1

    failure = result.failures[0]

    assert failure.handler is failing
    assert isinstance(failure.error, RuntimeError)
    assert str(failure.error) == "boom"


def test_publish_without_subscribers_succeeds_with_zero_deliveries() -> None:
    bus = EventBus()

    result = bus.publish(make_event())

    assert result.delivered == 0
    assert result.failures == ()
    assert result.succeeded is True

def test_handler_failure_emits_audit_failure_event() -> None:
    from ayeon.runtime.event_bus import EVENT_HANDLER_FAILED

    bus = EventBus()
    failure_events: list[AyeonEvent] = []

    def failing(event: AyeonEvent) -> None:
        raise RuntimeError("boom")

    bus.subscribe("runtime.test", failing)
    bus.subscribe(EVENT_HANDLER_FAILED, failure_events.append)

    original = make_event()
    result = bus.publish(original)

    assert result.succeeded is False
    assert len(failure_events) == 1

    failure_event = failure_events[0]

    assert failure_event.event_type == EVENT_HANDLER_FAILED
    assert failure_event.persistence is EventPersistence.AUDIT
    assert failure_event.payload["original_event_id"] == str(original.event_id)
    assert failure_event.payload["original_event_type"] == original.event_type
    assert failure_event.payload["error_type"] == "RuntimeError"
    assert failure_event.payload["error_message"] == "boom"


def test_failure_event_preserves_correlation_and_records_cause() -> None:
    from ayeon.runtime.event_bus import EVENT_HANDLER_FAILED

    bus = EventBus()
    failure_events: list[AyeonEvent] = []

    def failing(event: AyeonEvent) -> None:
        raise RuntimeError("boom")

    bus.subscribe("runtime.test", failing)
    bus.subscribe(EVENT_HANDLER_FAILED, failure_events.append)

    original = make_event()
    bus.publish(original)

    failure_event = failure_events[0]

    assert (
        failure_event.trace.correlation_id
        == original.trace.correlation_id
    )
    assert failure_event.trace.causation_id == original.event_id


def test_failure_handler_failure_does_not_recurse() -> None:
    from ayeon.runtime.event_bus import EVENT_HANDLER_FAILED

    bus = EventBus()
    failure_handler_calls = 0

    def original_failure(event: AyeonEvent) -> None:
        raise RuntimeError("original failure")

    def failure_event_failure(event: AyeonEvent) -> None:
        nonlocal failure_handler_calls
        failure_handler_calls += 1
        raise RuntimeError("failure while reporting failure")

    bus.subscribe("runtime.test", original_failure)
    bus.subscribe(EVENT_HANDLER_FAILED, failure_event_failure)

    result = bus.publish(make_event())

    assert result.succeeded is False
    assert len(result.failures) == 1
    assert failure_handler_calls == 1
