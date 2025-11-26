from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, Mapping, Optional


@dataclass
class IncomeSource:
    name: str
    income: float
    type: str  # e.g. "annually"
    taxable: Optional[bool] = None
    contributions: Mapping[str, float] = field(default_factory=dict)
    updated_at: Optional[str] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "IncomeSource":
        return cls(
            name=str(data.get("name", "")),
            income=float(data.get("income", 0.0)),
            type=str(data.get("type", "annually")),
            taxable=data.get("taxable"),
            contributions=data.get("contributions", {}) or {},
            updated_at=data.get("updated_at"),
        )

    def to_dict(self) -> Dict[str, Any]:
        data: Dict[str, Any] = {
            "name": self.name,
            "income": float(self.income),
            "type": self.type,
        }
        if self.taxable is not None:
            data["taxable"] = self.taxable
        if self.contributions:
            data["contributions"] = dict(self.contributions)
        if self.updated_at is not None:
            data["updated_at"] = self.updated_at
        return data



