from ayeon.contracts.action_attempt import ActionAttempt
from ayeon.contracts.action_execution import ActionExecution
from ayeon.contracts.action_execution_verification import (
    ActionExecutionVerification,
)
from ayeon.contracts.action_verification import ActionVerificationResult
from ayeon.contracts.actions import ActionIntent
from ayeon.contracts.authorization import (
    AuthorizationDecision,
    AuthorizationOutcome,
)
from ayeon.contracts.authorized_action import AuthorizedAction
from ayeon.contracts.common import ResultState, TraceContext
from ayeon.contracts.tool_execution import ToolExecutionResult
from ayeon.contracts.verification import VerificationState
from ayeon.verification.manager import (
    DuplicateVerifierError,
    VerificationManager,
    VerifierNotFoundError,
)


def make_execution() -> ActionExecution:
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
        reason="Authorized for verification manager test.",
    )

    authorized = AuthorizedAction(
        action=action,
        authorization=decision,
    )

    attempt = ActionAttempt(
        action_id=action.action_id,
        tool_name="fake_tool",
        trace=action.trace,
    )

    result = ToolExecutionResult(
        action_id=action.action_id,
        attempt_id=attempt.attempt_id,
        tool_name=attempt.tool_name,
        state=ResultState.SUCCESS,
        trace=attempt.trace,
        summary="Fake tool reported success.",
    )

    return ActionExecution(
        authorized_action=authorized,
        attempt=attempt,
        result=result,
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


def test_verification_manager_verifies_execution() -> None:
    verifier = FakeVerifier()
    manager = VerificationManager(verifiers=[verifier])
    execution = make_execution()

    result = manager.verify(execution)

    assert isinstance(result, ActionExecutionVerification)
    assert result.execution is execution
    assert result.verification.state is VerificationState.VERIFIED
    assert result.verification.verified_by == verifier.name
    assert verifier.calls == 1

def test_verification_manager_rejects_missing_verifier() -> None:
    verifier = FakeVerifier()
    manager = VerificationManager(verifiers=[verifier])

    action = ActionIntent(
        action_type="missing_tool",
        requested_by="cognition",
        trace=TraceContext.root(),
    )

    decision = AuthorizationDecision(
        action_id=action.action_id,
        outcome=AuthorizationOutcome.ALLOW,
        decided_by="authorization_policy",
        trace=action.trace,
        reason="Authorized for missing verifier test.",
    )

    authorized = AuthorizedAction(
        action=action,
        authorization=decision,
    )

    attempt = ActionAttempt(
        action_id=action.action_id,
        tool_name="missing_tool",
        trace=action.trace,
    )

    tool_result = ToolExecutionResult(
        action_id=action.action_id,
        attempt_id=attempt.attempt_id,
        tool_name=attempt.tool_name,
        state=ResultState.SUCCESS,
        trace=attempt.trace,
        summary="Missing-tool execution fixture.",
    )

    execution = ActionExecution(
        authorized_action=authorized,
        attempt=attempt,
        result=tool_result,
    )

    try:
        manager.verify(execution)
    except VerifierNotFoundError as exc:
        assert "missing_tool" in str(exc)
    else:
        raise AssertionError("Missing verifier must be rejected")

    assert verifier.calls == 0

def test_verification_manager_rejects_duplicate_verifier_names() -> None:
    first = FakeVerifier()
    second = FakeVerifier()

    try:
        VerificationManager(verifiers=[first, second])
    except DuplicateVerifierError as exc:
        assert "fake_tool" in str(exc)
    else:
        raise AssertionError("Duplicate verifier names must be rejected")

    assert first.calls == 0
    assert second.calls == 0

class BlankNameVerifier:
    @property
    def name(self) -> str:
        return "   "

    def verify(
        self,
        execution: ActionExecution,
    ) -> ActionVerificationResult:
        raise AssertionError("Blank-name verifier must never execute")


def test_verification_manager_rejects_blank_verifier_name() -> None:
    verifier = BlankNameVerifier()

    try:
        VerificationManager(verifiers=[verifier])
    except ValueError as exc:
        assert "name" in str(exc)
    else:
        raise AssertionError("Blank verifier name must be rejected")

class ExplodingVerifier:
    @property
    def name(self) -> str:
        return "fake_tool"

    def verify(
        self,
        execution: ActionExecution,
    ) -> ActionVerificationResult:
        raise RuntimeError("Simulated verifier failure")


def test_verification_manager_converts_verifier_exception_to_unknown() -> None:
    verifier = ExplodingVerifier()
    manager = VerificationManager(verifiers=[verifier])
    execution = make_execution()

    result = manager.verify(execution)

    assert result.execution is execution
    assert result.verification.action_id == execution.attempt.action_id
    assert result.verification.attempt_id == execution.attempt.attempt_id
    assert result.verification.state is VerificationState.UNKNOWN
    assert result.verification.verified_by == verifier.name

class WrongAttemptVerifier:
    @property
    def name(self) -> str:
        return "fake_tool"

    def verify(
        self,
        execution: ActionExecution,
    ) -> ActionVerificationResult:
        other_attempt = ActionAttempt(
            action_id=execution.attempt.action_id,
            tool_name=execution.attempt.tool_name,
            trace=execution.attempt.trace,
        )

        return ActionVerificationResult(
            action_id=execution.attempt.action_id,
            attempt_id=other_attempt.attempt_id,
            state=VerificationState.VERIFIED,
            verified_by=self.name,
            trace=execution.attempt.trace,
            reason="Returned verification for a different attempt.",
        )


def test_verification_manager_rejects_wrong_verification_attempt() -> None:
    manager = VerificationManager(verifiers=[WrongAttemptVerifier()])
    execution = make_execution()

    try:
        manager.verify(execution)
    except ValueError as exc:
        assert "attempt_id" in str(exc)
    else:
        raise AssertionError(
            "Verification for a different attempt must be rejected"
        )

class WrongIdentityVerifier:
    @property
    def name(self) -> str:
        return "fake_tool"

    def verify(
        self,
        execution: ActionExecution,
    ) -> ActionVerificationResult:
        return ActionVerificationResult(
            action_id=execution.attempt.action_id,
            attempt_id=execution.attempt.attempt_id,
            state=VerificationState.VERIFIED,
            verified_by="other_verifier",
            trace=execution.attempt.trace,
            reason="Verification with incorrect provenance.",
        )


def test_verification_manager_rejects_wrong_verifier_identity() -> None:
    manager = VerificationManager(verifiers=[WrongIdentityVerifier()])
    execution = make_execution()

    try:
        manager.verify(execution)
    except ValueError as exc:
        assert "verified_by" in str(exc)
    else:
        raise AssertionError(
            "Verifier must not claim a different verifier identity"
        )