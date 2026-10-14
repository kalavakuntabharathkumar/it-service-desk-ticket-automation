from pathlib import Path
import pandas as pd

output = Path("data/tickets.csv")
output.parent.mkdir(parents=True, exist_ok=True)
rows = [
    {"ticket_id": f"SD-{2000+i}", "created_at": f"2026-09-{1+(i%28):02d} {8+(i%9):02d}:{(i*7)%60:02d}",
     "team": ["Workplace", "Infrastructure", "Applications"][i%3],
     "category": ["Access", "Network", "Software", "Hardware", "Security"][i%5],
     "description": f"Synthetic service request example {i+1}",
     "status": ["Open", "In Progress", "Resolved"][i%3],
     "priority": ["Low", "Medium", "High", "Critical"][i%4],
     "sla_hours": [72, 24, 8, 4][i%4],
     "resolution_hours": (float([6, 15, 10, 2][i%4]) if i%3 == 2 else None),
     "assignee": ["A. Rao", "S. Iyer", "M. Shah", "R. Das"][i%4]}
    for i in range(120)
]
pd.DataFrame(rows).to_csv(output, index=False)
print(f"Wrote {len(rows)} synthetic tickets to {output}")
