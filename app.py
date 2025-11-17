"""
Admin app for the finance planner.

Usage:
source venv/bin/activate; streamlit run admin/app.py
"""


from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, Any, List
from datetime import datetime, timezone

import streamlit as st


APP_DIR = Path(__file__).resolve().parent
DATA_PATH = APP_DIR / "data.json"


def ensure_data_file_exists() -> None:
	"""
	Ensure data.json exists; stop execution if missing.
	"""
	if not DATA_PATH.exists():
		st.error(f"Missing data file: {DATA_PATH}. Please create it and retry.")
		st.stop()


def load_data() -> Dict[str, Any]:
	"""
	Load persisted app data from data.json; no in-code defaults.
	"""
	ensure_data_file_exists()
	try:
		with DATA_PATH.open("r") as f:
			data: Dict[str, Any] = json.load(f)
	except json.JSONDecodeError:
		st.error("Invalid JSON in data.json. Please fix the file contents.")
		st.stop()
	return data


def save_data(data: Dict[str, Any]) -> None:
	"""
	Persist the given data back to data.json.
	"""
	with DATA_PATH.open("w") as f:
		json.dump(data, f, indent=2)


def compute_compound_growth_series(
	principal: float,
	annual_rate_percent: float,
	years: int,
) -> List[float]:
	"""
	Compute annual compound growth values including year 0.
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


def compute_mortgage_monthly_payment(
	principal: float,
	annual_interest_percent: float,
	years: int,
) -> float:
	"""
	Fixed-rate mortgage monthly payment (principal & interest).
	Formula: M = P * r * (1+r)^n / ((1+r)^n - 1)
	r = monthly rate, n = total number of payments.
	"""
	if principal <= 0 or years <= 0:
		return 0.0
	monthly_rate = (annual_interest_percent / 100.0) / 12.0
	n = years * 12
	if monthly_rate == 0:
		return principal / n
	factor = (1.0 + monthly_rate) ** n
	return principal * monthly_rate * factor / (factor - 1.0)


def _assert_type(value: Any, expected_types: tuple) -> bool:
	return isinstance(value, expected_types)


def validate_data_or_stop(data: Dict[str, Any]) -> None:
	"""
	Validate required structure in data.json. Show errors and stop if invalid.
	"""
	errors: List[str] = []

	# Root keys
	required_root_keys = [
		"investments",
		"projection_horizon_years",
		"mortgage",
		"person1",
		"person2",
		"child1",
		"child2",
	]
	for key in required_root_keys:
		if key not in data:
			errors.append(f"Missing root key: {key}")

	# investments
	investments = data.get("investments")
	if not isinstance(investments, list) or len(investments) == 0:
		errors.append("investments must be a non-empty list")
	else:
		for idx, inv in enumerate(investments):
			if not isinstance(inv, dict):
				errors.append(f"investments[{idx}] must be an object")
				continue
			for k in ["name", "balance", "interest_rate_percent", "show_on_chart"]:
				if k not in inv:
					errors.append(f"investments[{idx}] missing key: {k}")
			if "name" in inv and not _assert_type(inv["name"], (str,)):
				errors.append(f"investments[{idx}].name must be a string")
			for k in ["balance", "interest_rate_percent"]:
				if k in inv and not _assert_type(inv[k], (int, float)):
					errors.append(f"investments[{idx}].{k} must be a number")
			if "show_on_chart" in inv and not _assert_type(inv["show_on_chart"], (bool,)):
				errors.append(f"investments[{idx}].show_on_chart must be a boolean")

	# projection_horizon_years
	if not _assert_type(data.get("projection_horizon_years"), (int,)):
		errors.append("projection_horizon_years must be an integer")

	# expenses
	expenses = data.get("expenses")
	if not isinstance(expenses, list):
		errors.append("expenses must be a list")
	else:
		for idx, exp in enumerate(expenses):
			if not isinstance(exp, dict):
				errors.append(f"expenses[{idx}] must be an object")
				continue
			for k in ["name", "expense", "type"]:
				if k not in exp:
					errors.append(f"expenses[{idx}] missing key: {k}")
			if "name" in exp and not _assert_type(exp["name"], (str,)):
				errors.append(f"expenses[{idx}].name must be a string")
			if "expense" in exp and not _assert_type(exp["expense"], (int, float)):
				errors.append(f"expenses[{idx}].expense must be a number")
			if "type" in exp and exp["type"] not in ("monthly", "annually"):
				errors.append(f"expenses[{idx}].type must be 'monthly' or 'annually'")

	# main projection config
	if not _assert_type(data.get("projection_years_main"), (int,)):
		errors.append("projection_years_main must be an integer")
	if not _assert_type(data.get("show_main_chart"), (bool,)):
		errors.append("show_main_chart must be a boolean")

	# mortgage
	mortgage = data.get("mortgage")
	if not isinstance(mortgage, dict):
		errors.append("mortgage must be an object")
	else:
		for k in [
			"home_price",
			"downpayment",
			"interest_rate_percent",
			"mortgage_duration_years",
			"annual_property_tax_percent",
			"start_year",
		]:
			if k not in mortgage:
				errors.append(f"mortgage missing key: {k}")
		for k in ["home_price", "downpayment", "interest_rate_percent", "annual_property_tax_percent"]:
			if k in mortgage and not _assert_type(mortgage[k], (int, float)):
				errors.append(f"mortgage.{k} must be a number")
		if "mortgage_duration_years" in mortgage and not _assert_type(mortgage["mortgage_duration_years"], (int,)):
			errors.append("mortgage.mortgage_duration_years must be an integer")
		if "start_year" in mortgage and not _assert_type(mortgage["start_year"], (int,)):
			errors.append("mortgage.start_year must be an integer")

	# adults
	for person_key in ["person1", "person2"]:
		person = data.get(person_key)
		if not isinstance(person, dict):
			errors.append(f"{person_key} must be an object")
			continue
		for k in [
			"annual_salary",
			"birth_year",
			"retirement_age",
			"retirement_401k_contribution",
			"social_security_start_year",
		]:
			if k not in person:
				errors.append(f"{person_key} missing key: {k}")
		for k in ["annual_salary", "retirement_401k_contribution"]:
			if k in person and not _assert_type(person[k], (int, float)):
				errors.append(f"{person_key}.{k} must be a number")
		for k in ["birth_year", "retirement_age", "social_security_start_year"]:
			if k in person and not _assert_type(person[k], (int,)):
				errors.append(f"{person_key}.{k} must be an integer")

	# children
	for child_key in ["child1", "child2"]:
		child = data.get(child_key)
		if not isinstance(child, dict):
			errors.append(f"{child_key} must be an object")
			continue
		for k in ["annual_529_contribution", "birth_year"]:
			if k not in child:
				errors.append(f"{child_key} missing key: {k}")
		if "annual_529_contribution" in child and not _assert_type(child["annual_529_contribution"], (int, float)):
			errors.append(f"{child_key}.annual_529_contribution must be a number")
		if "birth_year" in child and not _assert_type(child["birth_year"], (int,)):
			errors.append(f"{child_key}.birth_year must be an integer")

	if errors:
		st.error("Invalid data.json. Please fix the following issues:")
		for e in errors:
			st.write(f"- {e}")
		st.stop()


def main() -> None:
	st.set_page_config(page_title="Finance Planner", page_icon="💰", layout="centered")
	st.title("Finance Planner (Early Prototype)")
	st.caption("Configure people, children, investments, and mortgage. Charts show current balances.")

	data = load_data()
	validate_data_or_stop(data)

	chart_investments: List[Dict[str, Any]] = []
	with st.sidebar.form(key="inputs"):
		updated_investments: List[Dict[str, Any]] = []
		if "investments" in data and isinstance(data["investments"], list):
			with st.expander("Investments", expanded=False):
				projection_horizon_years = st.number_input(
					"Projection horizon (years)",
					min_value=1,
					max_value=100,
					value=int(data["projection_horizon_years"]),
					step=1,
					key="inv_horizon",
				)
				for idx, inv in enumerate(data["investments"]):
					name = str(inv["name"])
					balance = st.number_input(
						f"{name} balance",
						min_value=0.0,
						value=float(inv["balance"]),
						step=100.0,
						key=f"inv_balance_{idx}",
					)
					rate = st.number_input(
						f"{name} interest rate (%)",
						min_value=0.0,
						max_value=100.0,
						value=float(inv["interest_rate_percent"]),
						step=0.1,
						key=f"inv_rate_{idx}",
					)
					show_on_chart = st.checkbox(
						f"Show {name} on chart",
						value=bool(inv["show_on_chart"]),
						key=f"inv_show_{idx}",
					)
					chart_investments.append(
						{
							"name": name,
							"balance": float(balance),
							"interest_rate_percent": float(rate),
							"show": bool(show_on_chart),
						}
					)
					updated_investments.append(
						{
							"name": name,
							"balance": float(balance),
							"interest_rate_percent": float(rate),
							"show_on_chart": bool(show_on_chart),
							"updated_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
						}
					)
		# Expenses
		updated_expenses: List[Dict[str, Any]] = []
		with st.expander("Expenses", expanded=False):
			for idx, exp in enumerate(data["expenses"]):
				exp_name = st.text_input(
					f"Expense name #{idx+1}",
					value=str(exp["name"]),
					key=f"exp_name_{idx}",
				)
				exp_amount = st.number_input(
					f"{exp_name} amount",
					min_value=0.0,
					value=float(exp["expense"]),
					step=50.0,
					key=f"exp_amount_{idx}",
				)
				exp_type = st.selectbox(
					f"{exp_name} type",
					options=["monthly", "annually"],
					index=0 if exp["type"] == "monthly" else 1,
					key=f"exp_type_{idx}",
				)
				updated_expenses.append({"name": exp_name, "expense": float(exp_amount), "type": exp_type})
		# Mortgage
		if "mortgage" not in data:
			st.error("Missing 'mortgage' in data.json.")
			st.stop()
		mortgage_current = data["mortgage"]
		with st.expander("Mortgage", expanded=False):
			home_price = st.number_input(
				"Home price",
				min_value=0.0,
				value=float(mortgage_current["home_price"]),
				step=1000.0,
			)
			downpayment = st.number_input(
				"Down payment",
				min_value=0.0,
				value=float(mortgage_current["downpayment"]),
				step=1000.0,
			)
			mortgage_rate = st.number_input(
				"Mortgage interest rate (%)",
				min_value=0.0,
				max_value=100.0,
				value=float(mortgage_current["interest_rate_percent"]),
				step=0.1,
			)
			mortgage_years = st.number_input(
				"Mortgage duration (years)",
				min_value=1,
				max_value=50,
				value=int(mortgage_current["mortgage_duration_years"]),
				step=1,
			)
			property_tax_percent = st.number_input(
				"Annual property tax (%)",
				min_value=0.0,
				max_value=100.0,
				value=float(mortgage_current["annual_property_tax_percent"]),
				step=0.1,
			)
			mortgage_start_year = st.number_input(
				"Mortgage start year",
				min_value=1900,
				max_value=2100,
				value=int(mortgage_current["start_year"]),
				step=1,
			)
		with st.expander("Person 1", expanded=False):
			person1_salary = st.number_input(
				"Annual salary (Person 1)",
				min_value=0.0,
				value=float(data["person1"]["annual_salary"]),
				step=1000.0,
			)
			person1_birth_year = st.number_input(
				"Birth year (Person 1)",
				min_value=1900,
				max_value=2100,
				value=int(data["person1"]["birth_year"]),
				step=1,
			)
			person1_retirement_age = st.number_input(
				"Retirement age (Person 1)",
				min_value=0,
				max_value=100,
				value=int(data["person1"]["retirement_age"]),
				step=1,
			)
			person1_contribution = st.number_input(
				"Retirement contribution/year (Person 1)",
				min_value=0.0,
				value=float(data["person1"]["retirement_401k_contribution"]),
				step=1000.0,
			)
			person1_ss_start_year = st.number_input(
				"Social Security start year (Person 1)",
				min_value=0,
				max_value=120,
				value=int(data["person1"]["social_security_start_year"]),
				step=1,
			)
		with st.expander("Person 2", expanded=False):
			person2_salary = st.number_input(
				"Annual salary (Person 2)",
				min_value=0.0,
				value=float(data["person2"]["annual_salary"]),
				step=1000.0,
			)
			person2_birth_year = st.number_input(
				"Birth year (Person 2)",
				min_value=1900,
				max_value=2100,
				value=int(data["person2"]["birth_year"]),
				step=1,
			)
			person2_retirement_age = st.number_input(
				"Retirement age (Person 2)",
				min_value=0,
				max_value=100,
				value=int(data["person2"]["retirement_age"]),
				step=1,
			)
			person2_contribution = st.number_input(
				"Retirement contribution/year (Person 2)",
				min_value=0.0,
				value=float(data["person2"]["retirement_401k_contribution"]),
				step=1000.0,
			)
			person2_ss_start_year = st.number_input(
				"Social Security start year (Person 2)",
				min_value=0,
				max_value=120,
				value=int(data["person2"]["social_security_start_year"]),
				step=1,
			)
		with st.expander("Child 1", expanded=False):
			child1_529_contribution = st.number_input(
				"529 contribution/year (Child 1)",
				min_value=0.0,
				value=float(data["child1"]["annual_529_contribution"]),
				step=500.0,
			)
			child1_birth_year = st.number_input(
				"Birth year (Child 1)",
				min_value=1900,
				max_value=2100,
				value=int(data["child1"]["birth_year"]),
				step=1,
			)
		with st.expander("Child 2", expanded=False):
			child2_529_contribution = st.number_input(
				"529 contribution/year (Child 2)",
				min_value=0.0,
				value=float(data["child2"]["annual_529_contribution"]),
				step=500.0,
			)
			child2_birth_year = st.number_input(
				"Birth year (Child 2)",
				min_value=1900,
				max_value=2100,
				value=int(data["child2"]["birth_year"]),
				step=1,
			)

		# No 'years' dependency needed for investments anymore

		save_clicked = st.form_submit_button("Save & Update")

	if save_clicked:
		# Preserve existing nested fields (e.g., expiration_year) while updating known keys
		person1_current = dict(data["person1"])
		person1_current.update(
			{
				"annual_salary": float(person1_salary),
				"birth_year": int(person1_birth_year),
				"retirement_age": int(person1_retirement_age),
				"retirement_401k_contribution": float(person1_contribution),
				"social_security_start_year": int(person1_ss_start_year),
			}
		)
		person2_current = dict(data["person2"])
		person2_current.update(
			{
				"annual_salary": float(person2_salary),
				"birth_year": int(person2_birth_year),
				"retirement_age": int(person2_retirement_age),
				"retirement_401k_contribution": float(person2_contribution),
				"social_security_start_year": int(person2_ss_start_year),
			}
		)
		child1_current = dict(data["child1"])
		child1_current.update(
			{
				"annual_529_contribution": float(child1_529_contribution),
				"birth_year": int(child1_birth_year),
			}
		)
		child2_current = dict(data["child2"])
		child2_current.update(
			{
				"annual_529_contribution": float(child2_529_contribution),
				"birth_year": int(child2_birth_year),
			}
		)
		updates: Dict[str, Any] = {
			"person1": person1_current,
			"person2": person2_current,
			"child1": child1_current,
			"child2": child2_current,
		}
		if updated_investments:
			updates["investments"] = updated_investments
		if updated_expenses:
			# attach timestamps on each expense item
			exp_with_ts: List[Dict[str, Any]] = []
			for e in updated_expenses:
				e_ts = dict(e)
				e_ts["updated_at"] = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
				exp_with_ts.append(e_ts)
			updates["expenses"] = exp_with_ts
		updates["mortgage"] = {
			"home_price": float(home_price),
			"downpayment": float(downpayment),
			"interest_rate_percent": float(mortgage_rate),
			"mortgage_duration_years": int(mortgage_years),
			"annual_property_tax_percent": float(property_tax_percent),
			"start_year": int(mortgage_start_year),
			"updated_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
		}
		updates["projection_horizon_years"] = int(projection_horizon_years)
		# Attach updated_at to people/children blocks
		person1_current["updated_at"] = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
		person2_current["updated_at"] = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
		child1_current["updated_at"] = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
		child2_current["updated_at"] = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
		data.update(updates)
		save_data(data)
		st.success("Saved inputs to data.json")

	# Show current balances by investment (no years dependency)
	if "investments" in data:
		st.subheader("Balances by Investment")
		inv_names = [str(inv["name"]) for inv in data.get("investments", [])]
		inv_balances = [float(inv["balance"]) for inv in data.get("investments", [])]
		if inv_names:
			st.bar_chart({"Investment": inv_names, "Balance": inv_balances}, x="Investment", y="Balance")

	# Projected growth over time (based on sidebar horizon and toggles)
	if chart_investments:
		st.subheader("Projected Growth Over Time")
		series_by_investment: Dict[str, List[float]] = {}
		try:
			years = int(data["projection_horizon_years"])
		except KeyError:
			st.error("Missing 'projection_horizon_years' in data.json.")
			st.stop()
		for inv in chart_investments:
			if not inv.get("show"):
				continue
			name = str(inv["name"])
			series_by_investment[name] = compute_compound_growth_series(
				principal=float(inv["balance"]),
				annual_rate_percent=float(inv["interest_rate_percent"]),
				years=years,
			)
		if series_by_investment:
			st.line_chart(series_by_investment)

	# Main accumulated assets graph over projection_years_main, factoring expenses and stopping contributions at retirement age
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
		annual_child = float(data_dict["child1"]["annual_529_contribution"]) + float(data_dict["child2"]["annual_529_contribution"])
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

	if bool(data.get("show_main_chart", True)):
		try:
			main_series = compute_total_assets_series(data)
			st.subheader("Main: Accumulated Assets (All Accounts, Net of Expenses)")
			st.line_chart({"Year": list(range(0, len(main_series))), "Total Assets": main_series}, x="Year", y="Total Assets")
		except Exception as e:
			st.error(f"Failed to compute main accumulated assets series: {e}")

	# Mortgage summary
	if "mortgage" in data:
		m = data["mortgage"]
		principal = max(0.0, float(m["home_price"]) - float(m["downpayment"]))
		monthly_pi = compute_mortgage_monthly_payment(
			principal=principal,
			annual_interest_percent=float(m["interest_rate_percent"]),
			years=int(m["mortgage_duration_years"]),
		)
		monthly_tax = (float(m["home_price"]) * float(m["annual_property_tax_percent"]) / 100.0) / 12.0
		total_monthly = monthly_pi + monthly_tax
		st.subheader("Mortgage Summary")
		st.write(
			f"Principal: ${principal:,.0f} | Monthly P&I: ${monthly_pi:,.0f} | Monthly Tax: ${monthly_tax:,.0f} | Total Monthly: ${total_monthly:,.0f}"
		)

	with st.expander("View current data.json"):
		st.code(json.dumps(data, indent=2))


if __name__ == "__main__":
	main()


