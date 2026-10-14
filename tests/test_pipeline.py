import pandas as pd
import pytest

from src.pipeline import classify_sla_risk, get_summary, load_tickets

def sample_df():
    return pd.DataFrame([
        {"ticket_id":"A1","created_at":"2026-09-01 09:00","team":"Apps","category":"Software",
         "description":"Crash","status":"Resolved","priority":"High","sla_hours":8,
         "resolution_hours":10,"assignee":"Dev A"},
        {"ticket_id":"A2","created_at":"2026-09-01 10:00","team":"IT","category":"Access",
         "description":"Access","status":"Open","priority":"Low","sla_hours":72,
         "resolution_hours":None,"assignee":"Dev B"},
    ])

def test_classifies_breach_and_open_ticket():
    result = classify_sla_risk(sample_df())
    assert result["sla_breached"].tolist() == [True, False]
    assert result["is_open"].tolist() == [False, True]

def test_missing_columns_rejected():
    with pytest.raises(ValueError, match="Missing required columns"):
        classify_sla_risk(pd.DataFrame({"ticket_id":["A1"]}))

def test_load_and_summary(tmp_path):
    csv_path = tmp_path / "tickets.csv"
    db_path = tmp_path / "tickets.db"
    sample_df().to_csv(csv_path, index=False)
    assert load_tickets(csv_path, db_path) == 2
    summary = get_summary(db_path)
    assert summary["total"] == 2
    assert summary["open"] == 1
    assert summary["breached"] == 1
    assert summary["breach_rate"] == 50.0
