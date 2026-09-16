from ayeon.contracts.action_execution import ActionExecution
from ayeon.contracts.action_verification import ActionVerificationResult
from ayeon.verification.verifier import ActionVerifier


class FakeVerifier:
    @property
    def name(self) -> str:
        return "fake_verifier"

    def verify(
        self,
        execution: ActionExecution,
    ) -> ActionVerificationResult:
        raise NotImplementedError


def test_action_verifier_protocol_accepts_compatible_object() -> None:
    verifier = FakeVerifier()

    assert isinstance(verifier, ActionVerifier)
    assert verifier.name == "fake_verifier"


def test_action_verifier_protocol_rejects_incompatible_object() -> None:
    assert not isinstance(object(), ActionVerifier)