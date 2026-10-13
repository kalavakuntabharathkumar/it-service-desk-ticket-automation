# IT Service Desk Ticket Automation & Analytics System

A runnable portfolio implementation using Python, Pandas, SQLite, Streamlit, Plotly, Pytest, and GitHub Actions.

## Features
- Imports sample ticket data from CSV into SQLite.
- Assigns a priority and flags SLA risk using configurable rules.
- Provides searchable ticket triage and KPI charts in Streamlit.
- Includes tests for the data pipeline and metrics.
- Uses synthetic demo data. Resume metrics in the project brief are targets/context supplied by the author, not independently measured by this repository.

## Run locally
```bash
python -m venv .venv
# Linux/macOS
source .venv/bin/activate
# Windows PowerShell: .venv\Scripts\Activate.ps1
pip install -r requirements.txt
python scripts/generate_sample_data.py
python -m src.pipeline --input data/tickets.csv
streamlit run app.py
```

## Tests
```bash
pytest
```

SQLite database is created at `data/tickets.db`. The pipeline can be rerun safely; it replaces the imported `tickets` table from the CSV.
