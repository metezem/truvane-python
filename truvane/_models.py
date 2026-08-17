from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class VerifyResult:
    submission_id: str
    authentic: bool
    confidence: float
    manipulation_type: str | None

    @classmethod
    def _from_json(cls, data: dict[str, Any]) -> "VerifyResult":
        return cls(
            submission_id=data["submission_id"],
            authentic=data["authentic"],
            confidence=data["confidence"],
            manipulation_type=data.get("manipulation_type"),
        )
