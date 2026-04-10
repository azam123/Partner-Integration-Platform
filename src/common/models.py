"""Validation and canonical event models."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from typing import Any


@dataclass
class PartnerEnvelope:
    connector: str
    source_type: str
    record_id: str
    received_at: str
    payload: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def build_envelope(connector: str, source_type: str, record: dict[str, Any]) -> PartnerEnvelope:
    record_id = str(record.get("id") or record.get("record_id") or "")
    if not record_id:
        raise ValueError("record missing id")

    return PartnerEnvelope(
        connector=connector,
        source_type=source_type,
        record_id=record_id,
        received_at=datetime.now(timezone.utc).isoformat(),
        payload=record,
    )


def validate_envelope(data: dict[str, Any]) -> None:
    required_fields = ["connector", "source_type", "record_id", "received_at", "payload"]
    for field in required_fields:
        if field not in data:
            raise ValueError(f"missing required field: {field}")

    if not isinstance(data["payload"], dict):
        raise ValueError("payload must be an object")
