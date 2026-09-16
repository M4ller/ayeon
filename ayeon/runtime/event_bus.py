"""Typed in-process Event Bus for Ayeon Core."""

from __future__ import annotations

from collections import defaultdict
from collections.abc import Callable
from dataclasses import dataclass

from ayeon.contracts.events import AyeonEvent, EventPersistence

EventHandler = Callable[[AyeonEvent], None]

EVENT_HANDLER_FAILED = "runtime.event_handler_failed"
EVENT_BUS_SOURCE = "runtime.event_bus"


@dataclass(frozen=True, slots=True)
class HandlerFailure:
    """Failure produced by one event handler."""

    handler: EventHandler
    error: Exception


@dataclass(frozen=True, slots=True)
class PublishResult:
    """Structured result of one synchronous event dispatch."""

    delivered: int
    failures: tuple[HandlerFailure, ...]

    @property
    def succeeded(self) -> bool:
        """Return whether every attempted handler completed successfully."""

        return not self.failures


class EventBus:
    """Dispatches validated Ayeon events to in-process subscribers."""

    def __init__(self) -> None:
        self._subscribers: dict[str, list[EventHandler]] = defaultdict(list)

    def subscribe(
        self,
        event_type: str,
        handler: EventHandler,
    ) -> None:
        """Subscribe a handler to one event type."""

        if not event_type.strip():
            raise ValueError("event_type must not be empty")

        if handler not in self._subscribers[event_type]:
            self._subscribers[event_type].append(handler)

    def unsubscribe(
        self,
        event_type: str,
        handler: EventHandler,
    ) -> None:
        """Remove a handler from one event type."""

        handlers = self._subscribers.get(event_type)

        if handlers is None:
            return

        if handler in handlers:
            handlers.remove(handler)

        if not handlers:
            del self._subscribers[event_type]

    def publish(self, event: AyeonEvent) -> PublishResult:
        """Synchronously dispatch an event while isolating handler failures."""

        result = self._dispatch(event)

        if result.failures and event.event_type != EVENT_HANDLER_FAILED:
            self._publish_failure_events(event, result.failures)

        return result

    def _dispatch(self, event: AyeonEvent) -> PublishResult:
        handlers = tuple(self._subscribers.get(event.event_type, ()))
        failures: list[HandlerFailure] = []
        delivered = 0

        for handler in handlers:
            try:
                handler(event)
            except Exception as error:
                failures.append(
                    HandlerFailure(
                        handler=handler,
                        error=error,
                    )
                )
            else:
                delivered += 1

        return PublishResult(
            delivered=delivered,
            failures=tuple(failures),
        )

    def _publish_failure_events(
        self,
        original_event: AyeonEvent,
        failures: tuple[HandlerFailure, ...],
    ) -> None:
        for failure in failures:
            failure_event = AyeonEvent(
                event_type=EVENT_HANDLER_FAILED,
                source=EVENT_BUS_SOURCE,
                trace=original_event.trace.caused_by(original_event.event_id),
                persistence=EventPersistence.AUDIT,
                payload={
                    "original_event_id": str(original_event.event_id),
                    "original_event_type": original_event.event_type,
                    "handler": repr(failure.handler),
                    "error_type": type(failure.error).__name__,
                    "error_message": str(failure.error),
                },
            )

            self._dispatch(failure_event)
