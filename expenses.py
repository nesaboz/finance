from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional


@dataclass
class Expense:
    name: str
    expense: float
    type: str  # "monthly", "annually", or "total"
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    updated_at: Optional[str] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Expense":
        return cls(
            name=str(data.get("name", "")),
            expense=float(data.get("expense", 0.0)),
            type=str(data.get("type", "monthly")),
            start_date=data.get("start_date"),
            end_date=data.get("end_date"),
            updated_at=data.get("updated_at"),
        )

    def to_dict(self) -> Dict[str, Any]:
        data: Dict[str, Any] = {
            "name": self.name,
            "expense": float(self.expense),
            "type": self.type,
        }
        if self.start_date is not None:
            data["start_date"] = self.start_date
        if self.end_date is not None:
            data["end_date"] = self.end_date
        if self.updated_at is not None:
            data["updated_at"] = self.updated_at
        return data

    def annual_amount(self) -> float:
        """Return this expense's annualized amount under current simple rules."""
        if self.type == "monthly":
            return self.expense * 12.0
        # For "annually" and "total" we currently treat both as once per year
        return self.expense


def compute_annual_expenses(expenses: List[Expense]) -> float:
    return sum(e.annual_amount() for e in expenses)



