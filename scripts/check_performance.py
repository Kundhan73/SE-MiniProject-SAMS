"""Validate Locust aggregate latency/error evidence; no hardcoded pass counts."""

import csv
import json
from pathlib import Path
from datetime import datetime, timezone

rows = list(csv.DictReader(Path("docs/reports/load_stats.csv").open()))
row = next(r for r in rows if r["Name"] == "Aggregated")
requests = int(row["Request Count"])
failures = int(row["Failure Count"])
p95 = float(row["95%"])
result = {
    "generated_at": datetime.now(timezone.utc).isoformat(),
    "dataset_students": 2000,
    "dataset_faculty": 100,
    "concurrent_users": 20,
    "duration_seconds": 40,
    "requests": requests,
    "failures": failures,
    "p95_ms": p95,
    "passed": requests > 0 and failures == 0 and p95 <= 3000,
    "scope": "GitHub-hosted runner, PostgreSQL, 20 concurrent faculty sessions and reports; not a semester uptime or production capacity guarantee.",
}
Path("docs/reports/performance.json").write_text(json.dumps(result, indent=2) + "\n")
print(json.dumps(result, indent=2))
assert result["passed"], "Performance acceptance failed"
