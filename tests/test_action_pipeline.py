from ayeon.contracts.action_attempt import ActionAttempt
from ayeon.contracts.action_execution import ActionExecution
from ayeon.contracts.action_verification import ActionVerificationResult
from ayeon.contracts.actions import ActionIntent
from ayeon.contracts.authorization import (
    AuthorizationDecision,
    AuthorizationOutcome,
)
from ayeon.contracts.authorized_action import AuthorizedAction
from ayeon.contracts.common import ResultState, TraceContext
from ayeon.contracts.resolved_action_execution import ResolvedActionExecution
from ayeon.contracts.tool_execution import ToolExecutionResult
from ayeon.contracts.verification import VerificationState
from ayeon.runtime.action_pipeline import ActionPipeline
from ayeon.runtime.outcome_resolver import OutcomeResolver
from ayeon.tools.manager import ToolManager
from ayeon.verification.manager import VerificationManager


class FakeTool:
    def __init__(self) -> None:
        self.calls = 0

    @property
    def name(self) -> str:
        return "fake_tool"

    def execute(
        self,
        authorized_action: AuthorizedAction,
        attempt: ActionAttempt,
    ) -> ToolExecutionResult:
        self.calls += 1

        return ToolExecutionResult(
            action_id=authorized_action.action.action_id,
            attempt_id=attempt.attempt_id,
            tool_name=self.name,
            state=ResultState.SUCCESS,
            trace=attempt.trace,
            summary="Fake tool reported success.",
        )


class FakeVerifier:
    def __init__(self) -> None:
        self.calls = 0

    @property
    def name(self) -> str:
        return "fake_tool"

    def verify(
        self,
        execution: ActionExecution,
    ) -> ActionVerificationResult:
        self.calls += 1

        return ActionVerificationResult(
            action_id=execution.attempt.action_id,
            attempt_id=execution.attempt.attempt_id,
            state=VerificationState.VERIFIED,
            verified_by=self.name,
            trace=execution.attempt.trace,
            reason="Observed expected external effect.",
        )


def make_authorized_action() -> AuthorizedAction:
    action = ActionIntent(
        action_type="fake_tool",
        requested_by="cognition",
        trace=TraceContext.root(),
    )

    decision = AuthorizationDecision(
        action_id=action.action_id,
        outcome=AuthorizationOutcome.ALLOW,
        decided_by="authorization_policy",
        trace=action.trace,
        reason="Authorized for action pipeline test.",
    )

    return AuthorizedAction(
        action=action,
        authorization=decision,
    )


def test_action_pipeline_runs_authorized_action_to_final_outcome() -> None:
    tool = FakeTool()
    verifier = FakeVerifier()

    pipeline = ActionPipeline(
        tool_manager=ToolManager(tools=[tool]),
        verification_manager=VerificationManager(
            verifiers=[verifier],
        ),
        outcome_resolver=OutcomeResolver(),
    )

    authorized = make_authorized_action()

    resolved = pipeline.run(authorized)

    assert isinstance(resolved, ResolvedActionExecution)
    assert resolved.outcome.state is ResultState.SUCCESS
    assert (
        resolved.verified_execution.execution.authorized_action
        is authorized
    )
    assert tool.calls == 1
    assert verifier.calls == 1

class ExplodingTool:
    @property
    def name(self) -> str:
        return "fake_tool"

    def execute(
        self,
        authorized_action: AuthorizedAction,
        attempt: ActionAttempt,
    ) -> ToolExecutionResult:
        raise RuntimeError("Simulated tool failure")


def test_action_pipeline_preserves_unknown_tool_result() -> None:
    verifier = FakeVerifier()

    pipeline = ActionPipeline(
        tool_manager=ToolManager(tools=[ExplodingTool()]),
        verification_manager=VerificationManager(
            verifiers=[verifier],
        ),
        outcome_resolver=OutcomeResolver(),
    )

    resolved = pipeline.run(make_authorized_action())

    execution = resolved.verified_execution.execution

    assert execution.result.state is ResultState.UNKNOWN
    assert (
        resolved.verified_execution.verification.state
        is VerificationState.VERIFIED
    )
    assert resolved.outcome.state is ResultState.UNKNOWN
    assert verifier.calls == 1

class ExplodingVerifier:
    @property
    def name(self) -> str:
        return "fake_tool"

    def verify(
        self,
        execution: ActionExecution,
    ) -> ActionVerificationResult:
        raise RuntimeError("Simulated verifier failure")


def test_action_pipeline_preserves_unknown_verification() -> None:
    tool = FakeTool()

    pipeline = ActionPipeline(
        tool_manager=ToolManager(tools=[tool]),
        verification_manager=VerificationManager(
            verifiers=[ExplodingVerifier()],
        ),
        outcome_resolver=OutcomeResolver(),
    )

    resolved = pipeline.run(make_authorized_action())

    assert (
        resolved.verified_execution.execution.result.state
        is ResultState.SUCCESS
    )
    assert (
        resolved.verified_execution.verification.state
        is VerificationState.UNKNOWN
    )
    assert resolved.outcome.state is ResultState.UNKNOWN
    assert tool.calls == 1

def test_action_pipeline_propagates_missing_tool_error() -> None:
    from ayeon.tools.manager import ToolNotFoundError

    pipeline = ActionPipeline(
        tool_manager=ToolManager(tools=[]),
        verification_manager=VerificationManager(
            verifiers=[FakeVerifier()],
        ),
        outcome_resolver=OutcomeResolver(),
    )

    try:
        pipeline.run(make_authorized_action())
    except ToolNotFoundError:
        pass
    else:
        raise AssertionError(
            "Missing tool configuration must propagate as an error"
        )


def test_action_pipeline_propagates_missing_verifier_error() -> None:
    from ayeon.verification.manager import VerifierNotFoundError

    tool = FakeTool()

    pipeline = ActionPipeline(
        tool_manager=ToolManager(tools=[tool]),
        verification_manager=VerificationManager(verifiers=[]),
        outcome_resolver=OutcomeResolver(),
    )

    try:
        pipeline.run(make_authorized_action())
    except VerifierNotFoundError:
        pass
    else:
        raise AssertionError(
            "Missing verifier configuration must propagate as an error"
        )

    assert tool.calls == 1