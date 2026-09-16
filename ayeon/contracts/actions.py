"""Action intent contracts for Ayeon Core."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field
from datetime import datetime
from enum import StrEnum

from ayeon.contracts.common import (
    ActionId,
    TraceContext,
    new_action_id,
    utc_now,
)


class ActionRisk(StrEnum):
    """Estimated operational risk of a proposed action."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ActionReversibility(StrEnum):
    """Expected reversibility of an action."""

    REVERSIBLE = "reversible"
    PARTIALLY_REVERSIBLE = "partially_reversible"
    IRREVERSIBLE = "irreversible"
    UNKNOWN = "unknown"


@dataclass(frozen=True, slots=True)
class ActionIntent:
    """Proposal to perform an action.

    This object expresses intent only. It carries no authorization and
    provides no execution capability.
    """

    action_type: str
    requested_by: str
    trace: TraceContext
    parameters: Mapping[str, object] = field(default_factory=dict)
    risk: ActionRisk = ActionRisk.LOW
    reversibility: ActionReversibility = ActionReversibility.UNKNOWN
    reason: str | None = None
    action_id: ActionId = field(default_factory=new_action_id)
    created_at: datetime = field(default_factory=utc_now)

    def __post_init__(self) -> None:
        if not self.action_type.strip():
            raise ValueError("action_type must not be empty")

        if not self.requested_by.strip():
            raise ValueError("requested_by must not be empty")

        if self.created_at.tzinfo is None:
            raise ValueError("created_at must be timezone-aware")
