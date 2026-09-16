import pytest

from ayeon.contracts.common import TraceContext
from ayeon.contracts.errors import AyeonError, ErrorCategory, ErrorSeverity


def test_error_has_unique_id_and_traceability() -> None:
    trace = TraceContext.root()

    error = AyeonError(
        category=ErrorCategory.DEPENDENCY_FAILURE,
        severity=ErrorSeverity.ERROR,
        source="memory",
        message="Memory backend unavailable",
        recoverable=True,
        retryable=True,
        correlation_id=trace.correlation_id,
    )

    assert error.error_id is not None
    assert error.correlation_id == trace.correlation_id


def test_empty_source_is_rejected() -> None:
    with pytest.raises(ValueError, match="source must not be empty"):
        AyeonError(
            category=ErrorCategory.VALIDATION_ERROR,
            severity=ErrorSeverity.ERROR,
            source=" ",
            message="Invalid input",
            recoverable=True,
            retryable=False,
        )


def test_empty_message_is_rejected() -> None:
    with pytest.raises(ValueError, match="message must not be empty"):
        AyeonError(
            category=ErrorCategory.VALIDATION_ERROR,
            severity=ErrorSeverity.ERROR,
            source="contracts",
            message=" ",
            recoverable=True,
            retryable=False,
        )


def test_critical_error_cannot_be_blindly_retryable() -> None:
    with pytest.raises(
        ValueError,
        match="critical errors cannot be blindly marked retryable",
    ):
        AyeonError(
            category=ErrorCategory.INTEGRITY_ERROR,
            severity=ErrorSeverity.CRITICAL,
            source="continuity",
            message="Identity continuity could not be verified",
            recoverable=False,
            retryable=True,
        )
