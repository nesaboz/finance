from __future__ import annotations


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


