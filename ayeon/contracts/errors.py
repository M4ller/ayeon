"""Structured error contracts for Ayeon Core."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from uuid import UUID, uuid4

from ayeon.contracts.common import CorrelationId


class ErrorCategory(StrEnum):
    """Canonical categories for failures across Ayeon Core."""

    VALIDATION_ERROR = "validation_error"
    PERMISSION_DENIED = "permission_denied"
    CAPABILITY_UNAVAILABLE = "capability_unavailable"
    DEPENDENCY_FAILURE = "dependency_failure"
    TIMEOUT = "timeout"
    INTEGRITY_ERROR = "integrity_error"
    SECURITY_ERROR = "security_error"
    RESOURCE_EXHAUSTED = "resource_exhausted"
    CONFLICT = "conflict"
    UNKNOWN_ERROR = "unknown_error"


class ErrorSeverity(StrEnum):
    """Severity of a structured error."""

    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


@dataclass(frozen=True, slots=True)
class AyeonError:
    """Serializable domain error that preserves operational context."""

    category: ErrorCategory
    severity: ErrorSeverity
    source: str
    message: str
    recoverable: bool
    retryable: bool
    correlation_id: CorrelationId | None = None
    cause: str | None = None
    details: dict[str, object] = field(default_factory=dict)
    error_id: UUID = field(default_factory=uuid4)

    def __post_init__(self) -> None:
        if not self.source.strip():
            raise ValueError("source must not be empty")

        if not self.message.strip():
            raise ValueError("message must not be empty")

        if self.severity is ErrorSeverity.CRITICAL and self.retryable:
            raise ValueError(
                "critical errors cannot be blindly marked retryable"
            )
