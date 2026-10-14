from __future__ import annotations

import argparse
import sqlite3
from pathlib import Path

import pandas as pd

DEFAULT_DB = Path("data/tickets.db")
REQUIRED_COLUMNS = {
    "ticket_id", "created_at", "team", "category", "description", "status",
    "priority", "sla_hours", "resolution_hours", "assignee"
}

def classify_sla_risk(df: pd.DataFrame) -> pd.DataFrame:
    """Return a copy with normalized dates and an SLA-risk flag."""
    result = df.copy()
    missing = REQUIRED_COLUMNS - set(result.columns)
    if missing:
        raise ValueError(f"Missing required columns: {', '.join(sorted(missing))}")
    result["created_at"] = pd.to_datetime(result["created_at"], errors="coerce")
    result["sla_hours"] = pd.to_numeric(result["sla_hours"], errors="coerce")
    result["resolution_hours"] = pd.to_numeric(result["resolution_hours"], errors="coerce")
    if result["ticket_id"].isna().any():
        raise ValueError("ticket_id cannot be empty")
    result["sla_breached"] = (
        result["resolution_hours"].notna()
        & (result["resolution_hours"] > result["sla_hours"])
    )
    result["is_open"] = result["status"].str.lower().isin(["open", "in progress"])
    return result

def load_tickets(csv_path: str | Path, db_path: str | Path = DEFAULT_DB) -> int:
    """Validate and load a CSV into SQLite; returns number of loaded rows."""
    csv_path, db_path = Path(csv_path), Path(db_path)
    df = pd.read_csv(csv_path)
    df = classify_sla_risk(df)
    db_path.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(db_path) as conn:
        df.to_sql("tickets", conn, if_exists="replace", index=False)
        conn.execute("CREATE INDEX IF NOT EXISTS idx_tickets_status ON tickets(status)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_tickets_team ON tickets(team)")
    return len(df)

def get_summary(db_path: str | Path = DEFAULT_DB) -> dict:
    with sqlite3.connect(db_path) as conn:
        row = conn.execute(
            """SELECT COUNT(*),
                      SUM(CASE WHEN is_open = 1 THEN 1 ELSE 0 END),
                      SUM(CASE WHEN sla_breached = 1 THEN 1 ELSE 0 END),
                      AVG(CASE WHEN resolution_hours IS NOT NULL THEN resolution_hours END)
               FROM tickets"""
        ).fetchone()
    total, open_count, breached, avg_resolution = row
    total = total or 0
    return {
        "total": int(total),
        "open": int(open_count or 0),
        "breached": int(breached or 0),
        "breach_rate": (float(breached or 0) / total * 100) if total else 0.0,
        "avg_resolution_hours": float(avg_resolution or 0.0),
    }

def fetch_tickets(db_path: str | Path = DEFAULT_DB) -> pd.DataFrame:
    with sqlite3.connect(db_path) as conn:
        return pd.read_sql_query(
            "SELECT * FROM tickets ORDER BY created_at DESC, ticket_id", conn
        )

def main() -> None:
    parser = argparse.ArgumentParser(description="Load and validate service desk tickets.")
    parser.add_argument("--input", default="data/tickets.csv")
    parser.add_argument("--db", default=str(DEFAULT_DB))
    args = parser.parse_args()
    count = load_tickets(args.input, args.db)
    print(f"Loaded {count} tickets into {args.db}")

if __name__ == "__main__":
    main()
