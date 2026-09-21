"""Canonical serialization for persistable memory content."""

from __future__ import annotations

import json
import math
from collections.abc import Mapping

from ayeon.contracts.memory import MemoryRecord


def _validate_memory_value(value: object) -> None:
    if value is None or isinstance(value, str | bool | int):
        return

    if isinstance(value, float):
        if not math.isfinite(value):
            raise ValueError("memory content float must be finite")
        return

    if isinstance(value, Mapping):
        for key, nested_value in value.items():
            if not isinstance(key, str):
                raise TypeError("memory content mapping keys must be str")
            _validate_memory_value(nested_value)
        return

    if isinstance(value, list):
        for nested_value in value:
            _validate_memory_value(nested_value)
        return

    raise TypeError(
        "memory content contains unsupported value: "
        f"{type(value).__name__}"
    )


def encode_memory_content(content: Mapping[str, object]) -> bytes:
    """Encode memory content into deterministic canonical UTF-8 JSON."""

    _validate_memory_value(content)

    serialized = json.dumps(
        content,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    )
    return serialized.encode("utf-8")


def decode_memory_content(encoded: bytes) -> Mapping[str, object]:
    """Decode canonical UTF-8 JSON memory content."""

    def reject_non_finite(value: str) -> None:
        raise ValueError(f"non-finite JSON number: {value}")

    try:
        decoded = json.loads(
            encoded.decode("utf-8"),
            parse_constant=reject_non_finite,
        )
    except (UnicodeDecodeError, json.JSONDecodeError, ValueError) as exc:
        raise ValueError("invalid encoded memory content") from exc

    if not isinstance(decoded, dict):
        raise TypeError("decoded memory content must be a mapping")

    return decoded

def encode_memory_record(record: MemoryRecord) -> bytes:
    """Encode durable memory record identity and provenance canonically."""

    payload = {
        "memory_record_id": str(record.memory_record_id),
        "source_memory_intent_id": str(record.source_memory_intent_id),
        "created_at": record.created_at.isoformat(),
        "correlation_id": str(record.trace.correlation_id),
        "causation_id": (
            str(record.trace.causation_id)
            if record.trace.causation_id is not None
            else None
        ),
        "content": dict(record.content),
    }

    return encode_memory_content(payload)
