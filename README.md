## Finance Planner (Streamlit)

Minimal prototype to visualize annual compound growth with inputs persisted in `data.json`.

### Setup
1. Create/activate a virtual environment (optional but recommended).
2. Install dependencies:
   ```
   pip install -r /home/nbozinovic/dev/admin/requirements.txt
   ```

### Run
```
streamlit run /home/nbozinovic/dev/admin/app.py
```

The app reads and writes `/home/nbozinovic/dev/admin/data.json`.

### Notes
- Current UI captures:
  - Initial amount (principal)
  - Annual interest rate (%)
  - Years are fixed at the stored value (default 30) for now
- Roadmap items (to be added next):
  - Inputs for salary, bonus, stocks, and strike prices
  - Configurable years and contribution scenarios


