from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Dict, List

from expenses import Expense, compute_annual_expenses
from investments import Investment
from people import Child, Person


@dataclass
class FinancePlan:
    investments: List[Investment]
    expenses: List[Expense]
    person1: Person
    person2: Person
    child1: Child
    child2: Child
    projection_years_main: int

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "FinancePlan":
        investments = [Investment.from_dict(inv) for inv in data.get("investments", [])]
        expenses = [Expense.from_dict(exp) for exp in data.get("expenses", [])]
        person1 = Person.from_dict(data.get("person1", {}))
        person2 = Person.from_dict(data.get("person2", {}))
        child1 = Child.from_dict(data.get("child1", {}))
        child2 = Child.from_dict(data.get("child2", {}))
        projection_years_main = int(data.get("projection_years_main", 0))
        return cls(
            investments=investments,
            expenses=expenses,
            person1=person1,
            person2=person2,
            child1=child1,
            child2=child2,
            projection_years_main=projection_years_main,
        )

    def to_dict(self) -> Dict[str, Any]:
        """Convert back to the flat dict structure expected in data.json."""
        data: Dict[str, Any] = {
            "investments": [inv.to_dict() for inv in self.investments],
            "expenses": [exp.to_dict() for exp in self.expenses],
            "person1": self.person1.to_dict(),
            "person2": self.person2.to_dict(),
            "child1": self.child1.to_dict(),
            "child2": self.child2.to_dict(),
            "projection_years_main": int(self.projection_years_main),
        }
        return data

    def total_assets_series(self) -> List[float]:
        """Mirror of the existing compute_total_assets_series logic, but on objects."""
        years_main = int(self.projection_years_main)
        balances = [float(inv.balance) for inv in self.investments]
        rates = [float(inv.interest_rate_percent) / 100.0 for inv in self.investments]
        cash = 0.0
        current_year = datetime.now(timezone.utc).year

        def years_remaining_to_retirement(person: Person) -> int:
            age = current_year - int(person.birth_year)
            return max(0, int(person.retirement_age) - age)

        p1_years = years_remaining_to_retirement(self.person1)
        p2_years = years_remaining_to_retirement(self.person2)
        annual_p1 = float(self.person1.retirement_401k_contribution)
        annual_p2 = float(self.person2.retirement_401k_contribution)
        annual_child = float(self.child1.annual_529_contribution) + float(
            self.child2.annual_529_contribution
        )
        annual_exp = compute_annual_expenses(self.expenses)

        series: List[float] = []
        total0 = sum(balances) + cash
        series.append(total0)

        for year_idx in range(1, years_main + 1):
            contri = 0.0
            if year_idx <= p1_years:
                contri += annual_p1
            if year_idx <= p2_years:
                contri += annual_p2
            contri += annual_child

            cash += contri
            cash -= annual_exp

            for i in range(len(balances)):
                balances[i] = balances[i] * (1.0 + rates[i])
            series.append(sum(balances) + cash)
        return series


def compute_time_series(data: Dict[str, Any], horizon_years: int) -> Dict[str, List[float]]:
    """
    Compute yearly series for Investments, Income, and Expenses over the given horizon.

    This centralizes domain logic outside the Streamlit app.
    """
    current_year = datetime.now(timezone.utc).year
    years: List[int] = [current_year + i for i in range(horizon_years + 1)]

    # Investments: use Investment dataclass and its growth logic
    investments_data = data.get("investments", [])
    investments = [Investment.from_dict(inv) for inv in investments_data]
    if investments:
        per_investment = [inv.growth_series(horizon_years) for inv in investments]
        investment_series = [sum(vals) for vals in zip(*per_investment)]
    else:
        investment_series = [0.0] * (horizon_years + 1)

    # Income: work directly from raw dicts, honoring optional start/end dates,
    # and apply effective_tax_rate_percent when present.
    income_items = data.get("income", [])
    net_income_series: List[float] = []
    for year in years:
        net_income = 0.0
        for item in income_items:
            amount = float(item.get("income", 0.0))
            start_date = item.get("start_date")
            end_date = item.get("end_date")

            if start_date:
                try:
                    start_year = int(str(start_date)[:4])
                except ValueError:
                    start_year = None
            else:
                start_year = None

            if end_date:
                try:
                    end_year = int(str(end_date)[:4])
                except ValueError:
                    end_year = None
            else:
                end_year = None

            if start_year is not None and year < start_year:
                continue
            if end_year is not None and year > end_year:
                continue

            tax_rate_pct = float(item.get("effective_tax_rate_percent", 0.0))
            tax_rate = tax_rate_pct / 100.0
            net_amount = amount * (1.0 - tax_rate)
            net_income += net_amount
        net_income_series.append(net_income)

    # Expenses: same pattern, but annualized by type and respecting start/end
    expenses_data = data.get("expenses", [])
    expense_series: List[float] = []
    for year in years:
        total_expenses = 0.0
        for exp in expenses_data:
            amount = float(exp.get("expense", 0.0))
            exp_type = str(exp.get("type", "monthly"))
            start_date = exp.get("start_date")
            end_date = exp.get("end_date")

            if start_date:
                try:
                    start_year = int(str(start_date)[:4])
                except ValueError:
                    start_year = None
            else:
                start_year = None

            if end_date:
                try:
                    end_year = int(str(end_date)[:4])
                except ValueError:
                    end_year = None
            else:
                end_year = None

            if start_year is not None and year < start_year:
                continue
            if end_year is not None and year > end_year:
                continue

            if exp_type == "monthly":
                annual_amount = amount * 12.0
            else:
                # "annually" or "total" treated as once per year while active
                annual_amount = amount

            total_expenses += annual_amount
        expense_series.append(total_expenses)

    # Net income after tax and expenses, then cumulative over time
    net_after_expenses_series: List[float] = []
    for i in range(len(years)):
        net_after_expenses_series.append(net_income_series[i] - expense_series[i])

    cumulative_net_series: List[float] = []
    running = 0.0
    for value in net_after_expenses_series:
        running += value
        cumulative_net_series.append(running)

    return {
        "Year": years,
        "Investments": investment_series,
        "Income": cumulative_net_series,
        "Expenses": expense_series,
    }




