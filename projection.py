from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, List


def compute_annual_expenses(expenses_list: List[Dict[str, Any]]) -> float:
	total = 0.0
	for e in expenses_list:
		if e["type"] == "monthly":
			total += float(e["expense"]) * 12.0
		else:
			total += float(e["expense"])
	return total


def compute_total_assets_series(data_dict: Dict[str, Any]) -> List[float]:
	years_main = int(data_dict["projection_years_main"])
	investments_list = data_dict["investments"]
	# Copy balances to mutable list
	balances = [float(inv["balance"]) for inv in investments_list]
	rates = [float(inv["interest_rate_percent"]) / 100.0 for inv in investments_list]
	cash = 0.0
	current_year = datetime.now(timezone.utc).year

	# Contribution windows
	def years_remaining_to_retirement(person: Dict[str, Any]) -> int:
		age = current_year - int(person["birth_year"])
		return max(0, int(person["retirement_age"]) - age)

	p1_years = years_remaining_to_retirement(data_dict["person1"])
	p2_years = years_remaining_to_retirement(data_dict["person2"])
	annual_p1 = float(data_dict["person1"]["retirement_401k_contribution"])
	annual_p2 = float(data_dict["person2"]["retirement_401k_contribution"])
	annual_child = float(data_dict["child1"]["annual_529_contribution"]) + float(
		data_dict["child2"]["annual_529_contribution"]
	)
	annual_exp = compute_annual_expenses(data_dict["expenses"])
	series: List[float] = []
	total0 = sum(balances) + cash
	series.append(total0)

	for year_idx in range(1, years_main + 1):
		# Contributions stop at retirement
		contri = 0.0
		if year_idx <= p1_years:
			contri += annual_p1
		if year_idx <= p2_years:
			contri += annual_p2
		contri += annual_child
		# Update cash with contributions and expenses
		cash += contri
		cash -= annual_exp
		# Grow investments
		for i in range(len(balances)):
			balances[i] = balances[i] * (1.0 + rates[i])
		series.append(sum(balances) + cash)
	return series


