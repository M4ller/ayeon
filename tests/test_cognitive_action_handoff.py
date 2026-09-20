"""Tests for cognitive action handoff."""

from ayeon.contracts.actions import ActionIntent
from ayeon.contracts.authorization import AuthorizationRequest
from ayeon.contracts.cognition import CognitiveOutput
from ayeon.contracts.common import TraceContext
from ayeon.core.cognition.action_handoff import CognitiveActionHandoff
from ayeon.runtime.executive import Executive


def make_action(
    *,
    trace: TraceContext,
    action_type: str,
) -> ActionIntent:
    return ActionIntent(
        action_type=action_type,
        requested_by="cognition",
        trace=trace,
    )


def test_handoff_creates_authorization_request_for_each_action_intent() -> None:
    trace = TraceContext.root()
    first = make_action(trace=trace, action_type="test.first")
    second = make_action(trace=trace, action_type="test.second")
    output = CognitiveOutput(
        trace=trace,
        action_intents=(first, second),
    )
    handoff = CognitiveActionHandoff(executive=Executive())

    requests = handoff.prepare_authorization_requests(output)

    assert isinstance(requests, tuple)
    assert len(requests) == 2
    assert all(isinstance(request, AuthorizationRequest) for request in requests)
    assert requests[0].action is first
    assert requests[1].action is second


def test_handoff_preserves_action_order() -> None:
    trace = TraceContext.root()
    first = make_action(trace=trace, action_type="test.first")
    second = make_action(trace=trace, action_type="test.second")
    output = CognitiveOutput(
        trace=trace,
        action_intents=(first, second),
    )
    handoff = CognitiveActionHandoff(executive=Executive())

    requests = handoff.prepare_authorization_requests(output)

    assert tuple(request.action for request in requests) == (first, second)


def test_handoff_returns_empty_tuple_when_no_actions_are_proposed() -> None:
    output = CognitiveOutput(
        trace=TraceContext.root(),
        spoken_response="No action required.",
    )
    handoff = CognitiveActionHandoff(executive=Executive())

    requests = handoff.prepare_authorization_requests(output)

    assert requests == ()


def test_handoff_exposes_no_execution_or_authorization_methods() -> None:
    handoff = CognitiveActionHandoff(executive=Executive())

    assert not hasattr(handoff, "execute")
    assert not hasattr(handoff, "run")
    assert not hasattr(handoff, "authorize")
    assert not hasattr(handoff, "allow")
    assert not hasattr(handoff, "approve")


class RecordingExecutive:
    """Record action intents delegated through the executive boundary."""

    def __init__(self) -> None:
        self.received_actions = []

    def request_authorization(
        self,
        action: ActionIntent,
    ) -> AuthorizationRequest:
        self.received_actions.append(action)
        return AuthorizationRequest(
            action=action,
            trace=action.trace,
        )


def test_handoff_delegates_each_action_to_executive() -> None:
    trace = TraceContext.root()
    first = make_action(trace=trace, action_type="test.first")
    second = make_action(trace=trace, action_type="test.second")
    output = CognitiveOutput(
        trace=trace,
        action_intents=(first, second),
    )
    executive = RecordingExecutive()
    handoff = CognitiveActionHandoff(executive=executive)

    handoff.prepare_authorization_requests(output)

    assert executive.received_actions == [first, second]


def test_handoff_preserves_cognitive_trace_correlation() -> None:
    trace = TraceContext.root()
    action = make_action(
        trace=trace,
        action_type="test.correlated",
    )
    output = CognitiveOutput(
        trace=trace,
        action_intents=(action,),
    )
    handoff = CognitiveActionHandoff(executive=Executive())

    requests = handoff.prepare_authorization_requests(output)

    assert requests[0].trace.correlation_id == output.trace.correlation_id
    assert requests[0].action.trace.correlation_id == output.trace.correlation_id


def test_handoff_preserves_action_identity() -> None:
    trace = TraceContext.root()
    action = make_action(
        trace=trace,
        action_type="test.identity",
    )
    output = CognitiveOutput(
        trace=trace,
        action_intents=(action,),
    )
    handoff = CognitiveActionHandoff(executive=Executive())

    requests = handoff.prepare_authorization_requests(output)

    assert requests[0].action is action
    assert requests[0].action.action_id == action.action_id
