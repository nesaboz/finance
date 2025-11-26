## Finance Planner (Streamlit)

Simple finance planner to explore how **investments** and **cashflow (income − taxes − expenses)** evolve over time.

All configuration lives in `data.json`; the Streamlit app is intentionally UI‑only and delegates logic to small domain modules.

### Setup

1. (Optional) Create and activate a virtual environment:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

### Run the app

From the project root:

```bash
streamlit run app.py
```

The app reads and writes `data.json` in the project root.

### What the app shows

- **Single time‑series chart**
  - X‑axis is **calendar year**, starting from the current year.
  - You choose the horizon in the left sidebar: **1, 5, 10, 30, or 50 years**.
  - The chart plots:
    - **Investments**: total portfolio value over time assuming simple annual compound growth per account.
    - **Profit**: cumulative net income after **taxes and expenses**.

- **Raw JSON viewer & editor**
  - `View current data.json` expander: pretty‑printed read‑only JSON.
  - `Edit data.json` expander: editable JSON text area with a **Save** button; saves only if the JSON parses.

### Data model (high level)

All of this is stored in `data.json` and mapped to small dataclasses in `investments.py`, `expenses.py`, `income.py`, and `people.py`.

- **Investments**
  - Fields per entry (not exhaustive): `name`, `balance`, `interest_rate_percent`, `show_on_chart`, optional metadata like `taxable`, `broker`.
  - Logic:
    - `Investment.growth_series(years)` uses `compute_compound_growth_series` to return the value for each year `t` using:
      \[
      \text{value}_t = \text{balance} \times (1 + r)^t
      \]

- **Expenses**
  - Fields: `name`, `expense`, `type` (`"monthly"`, `"annually"`, `"total"`), optional `start_date`, `end_date`.
  - Logic:
    - Annualized via `Expense.annual_amount()`:
      - `"monthly"` → `expense * 12`
      - `"annually"` / `"total"` → `expense` once per active year
    - Optional `start_date` / `end_date` (year taken from first 4 chars) bound when the expense is active (e.g., university for 4 years).

- **Income**
  - Fields: `name`, `income`, `type`, optional `effective_tax_rate_percent`, optional `start_date` / `end_date`.
  - Logic:
    - In each year, if the income item is active, net income is:
      \[
      \text{net} = \text{income} \times (1 - \text{effective\_tax\_rate\_percent} / 100)
      \]

- **Profit and investments over time**
  - Implemented in `plan.py` via `compute_time_series(data, horizon_years)`:
    - Builds `Year` axis from the current year out to the selected horizon.
    - `Investments` series: sum of each `Investment.growth_series(horizon_years)` across all investments.
    - `Income` series:
      - For each year: sum **net income after tax** for all active income sources.
      - Subtract that year’s **total expenses**.
      - Accumulate over time, so the plotted **Profit** is *cumulative* net of taxes and expenses.

### Code layout

- `app.py` – Streamlit UI only (sidebar horizon selector, chart, JSON viewer/editor).
- `data_io.py` – load/save helpers for `data.json`.
- `investments.py` – `Investment` dataclass and compound‑growth helper.
- `expenses.py` – `Expense` dataclass and annualization helpers.
- `income.py` – `IncomeSource` dataclass.
- `people.py` – `Person` / `Child` dataclasses for future richer modeling.
- `plan.py` – `FinancePlan` and `compute_time_series` (all cross‑cutting time‑series math).

