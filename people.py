from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Optional


@dataclass
class Person:
    name: str
    birth_year: int
    retirement_age: int
    social_security_start_year: int
    annual_salary: float = 0.0
    retirement_401k_contribution: float = 0.0
    expiration_age: Optional[int] = None
    updated_at: Optional[str] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Person":
        return cls(
            name=str(data.get("name", "")),
            birth_year=int(data.get("birth_year", 0)),
            retirement_age=int(data.get("retirement_age", 65)),
            social_security_start_year=int(data.get("social_security_start_year", 67)),
            annual_salary=float(data.get("annual_salary", 0.0)),
            retirement_401k_contribution=float(data.get("retirement_401k_contribution", 0.0)),
            expiration_age=data.get("expiration_age"),
            updated_at=data.get("updated_at"),
        )

    def to_dict(self) -> Dict[str, Any]:
        data: Dict[str, Any] = {
            "name": self.name,
            "birth_year": int(self.birth_year),
            "retirement_age": int(self.retirement_age),
            "social_security_start_year": int(self.social_security_start_year),
            "annual_salary": float(self.annual_salary),
            "retirement_401k_contribution": float(self.retirement_401k_contribution),
        }
        if self.expiration_age is not None:
            data["expiration_age"] = int(self.expiration_age)
        if self.updated_at is not None:
            data["updated_at"] = self.updated_at
        return data


@dataclass
class Child:
    name: str
    birth_year: int
    annual_529_contribution: float = 0.0
    updated_at: Optional[str] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Child":
        return cls(
            name=str(data.get("name", "")),
            birth_year=int(data.get("birth_year", 0)),
            annual_529_contribution=float(data.get("annual_529_contribution", 0.0)),
            updated_at=data.get("updated_at"),
        )

    def to_dict(self) -> Dict[str, Any]:
        data: Dict[str, Any] = {
            "name": self.name,
            "birth_year": int(self.birth_year),
            "annual_529_contribution": float(self.annual_529_contribution),
        }
        if self.updated_at is not None:
            data["updated_at"] = self.updated_at
        return data



