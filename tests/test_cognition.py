import pytest

from ayeon.contracts.actions import ActionIntent
from ayeon.contracts.cognition import CognitiveOutput
from ayeon.contracts.common import TraceContext


def test_cognitive_output_can_speak_without_acting() -> None:
    output = CognitiveOutput(
        trace=TraceContext.root(),
        spoken_response="Hola, Felipe.",
    )

    assert output.spoken_response == "Hola, Felipe."
    assert output.action_intents == ()


def test_cognitive_output_can_propose_action_without_authorizing_it() -> None:
    trace = TraceContext.root()

    intent = ActionIntent(
        action_type="file.read",
        requested_by="cognition",
        trace=trace,
    )

    output = CognitiveOutput(
        trace=trace,
        action_intents=(intent,),
    )

    assert output.action_intents == (intent,)
    assert not hasattr(output, "authorized")
    assert not hasattr(output, "authorization")
    assert not hasattr(output, "permission")


def test_cognitive_output_has_no_execution_capability() -> None:
    output = CognitiveOutput(trace=TraceContext.root())

    assert not hasattr(output, "execute")
    assert not hasattr(output, "run")
    assert not hasattr(output, "tool_manager")


def test_action_intent_must_share_correlation_id() -> None:
    output_trace = TraceContext.root()
    unrelated_trace = TraceContext.root()

    intent = ActionIntent(
        action_type="file.read",
        requested_by="cognition",
        trace=unrelated_trace,
    )

    with pytest.raises(
        ValueError,
        match="action intent must share CognitiveOutput correlation_id",
    ):
        CognitiveOutput(
            trace=output_trace,
            action_intents=(intent,),
        )


def test_blank_spoken_response_is_rejected() -> None:
    with pytest.raises(ValueError, match="spoken_response must not be blank"):
        CognitiveOutput(
            trace=TraceContext.root(),
            spoken_response=" ",
        )


def test_cognitive_output_copies_mutable_mapping_inputs() -> None:
    emotional_update = {"mood": "calm"}
    attention_update = {"focus": "user"}
    avatar_state = {"expression": "neutral"}
    memory_intent = {"kind": "observation"}

    output = CognitiveOutput(
        trace=TraceContext.root(),
        memory_intents=(memory_intent,),
        emotional_update=emotional_update,
        attention_update=attention_update,
        avatar_state=avatar_state,
    )

    emotional_update["mood"] = "angry"
    attention_update["focus"] = "other"
    avatar_state["expression"] = "angry"
    memory_intent["kind"] = "changed"

    assert output.emotional_update["mood"] == "calm"
    assert output.attention_update["focus"] == "user"
    assert output.avatar_state["expression"] == "neutral"
    assert output.memory_intents[0]["kind"] == "observation"


def test_cognitive_output_mapping_fields_are_read_only() -> None:
    output = CognitiveOutput(
        trace=TraceContext.root(),
        memory_intents=({"kind": "observation"},),
        emotional_update={"mood": "calm"},
        attention_update={"focus": "user"},
        avatar_state={"expression": "neutral"},
    )

    mappings = (
        output.memory_intents[0],
        output.emotional_update,
        output.attention_update,
        output.avatar_state,
    )

    for mapping in mappings:
        try:
            mapping["mutated"] = True
        except TypeError:
            pass
        else:
            raise AssertionError("CognitiveOutput mappings must be read-only")
