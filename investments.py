from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional


@dataclass
class Investment:
    name: str
    balance: float
    interest_rate_percent: float
    show_on_chart: bool = True
    # Extra, optional metadata from JSON (ignored by calculations but preserved)
    taxable: Optional[bool] = None
    broker: Optional[str] = None
    updated_at: Optional[str] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Investment":
        return cls(
            name=str(data.get("name", "")),
            balance=float(data.get("balance", 0.0)),
            interest_rate_percent=float(data.get("interest_rate_percent", 0.0)),
            show_on_chart=bool(data.get("show_on_chart", True)),
            taxable=data.get("taxable"),
            broker=data.get("broker"),
            updated_at=data.get("updated_at"),
        )

    def to_dict(self) -> Dict[str, Any]:
        data: Dict[str, Any] = {
            "name": self.name,
            "balance": float(self.balance),
            "interest_rate_percent": float(self.interest_rate_percent),
            "show_on_chart": bool(self.show_on_chart),
        }
        if self.taxable is not None:
            data["taxable"] = self.taxable
        if self.broker is not None:
            data["broker"] = self.broker
        if self.updated_at is not None:
            data["updated_at"] = self.updated_at
        return data

    def growth_series(self, years: int) -> List[float]:
        """Convenience wrapper around compute_compound_growth_series."""
        return compute_compound_growth_series(
            principal=self.balance,
            annual_rate_percent=self.interest_rate_percent,
            years=years,
        )


def compute_compound_growth_series(
    principal: float,
    annual_rate_percent: float,
    years: int,
) -> List[float]:
    """Compute annual compound growth values including year 0.

    Returns a list of length years + 1 where index t is value at year t.
    """
    annual_rate = annual_rate_percent / 100.0
    values: List[float] = []
    current_value = float(principal)
    for year in range(0, years + 1):
        if year == 0:
            values.append(current_value)
        else:
            current_value = current_value * (1.0 + annual_rate)
            values.append(current_value)
    return values
