"""
Admin app for the finance planner.

Usage:
source venv/bin/activate; streamlit run admin/app.py
"""


from __future__ import annotations

import json
from typing import Any, Dict, List
import streamlit as st

from data_io import load_data, save_data
from plan import compute_time_series


def main() -> None:
	st.set_page_config(page_title="Finance Planner", page_icon="💰", layout="centered")
	st.title("Finance Planner")
	st.caption("Time-series view of income and investments.")

	data: Dict[str, Any] = load_data()

	# Sidebar: projection horizon
	horizon_options = [1, 5, 10, 30, 50]
	horizon_years = st.sidebar.selectbox(
		"Projection horizon (years)",
		horizon_options,
		index=2,  # default to 10 years
	)

	series = compute_time_series(data, horizon_years)

	# Plot profit = net income after tax minus expenses (as "Income" series)
	# alongside total Investments over time.
	if any(series.get("Income", [])) or any(series.get("Investments", [])):
		st.subheader("Profit and Investments Over Time")
		chart = {
			"Year": series["Year"],
			"Profit": series["Income"],
			"Investments": series["Investments"],
		}
		st.line_chart(chart, x="Year", y=["Profit", "Investments"])

	with st.expander("View current data.json"):
		st.code(json.dumps(data, indent=2))

	with st.expander("Edit data.json"):
		edited_text = st.text_area(
			"Raw data.json",
			value=json.dumps(data, indent=4),
			height=400,
		)
		if st.button("Save data.json"):
			try:
				new_data = json.loads(edited_text)
			except json.JSONDecodeError as e:
				st.error(f"Invalid JSON, not saved: {e}")
			else:
				save_data(new_data)
				st.success("data.json saved. The app will use the new values on next run.")


if __name__ == "__main__":
	main()


