"""Boundary checks for the sustained-load acceptance gate."""

import csv
import json
import subprocess
import sys
from pathlib import Path

import pytest


@pytest.mark.parametrize("latency,accepted", [(2999, True), (3000, False), (3001, False)])
def test_load_gate_requires_p95_strictly_below_three_seconds(tmp_path, latency, accepted):
    fields = [
        "Type",
        "Name",
        "Request Count",
        "Failure Count",
        "95%",
        "Average Response Time",
        "Max Response Time",
    ]
    with (tmp_path / "perf_stats.csv").open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for name in ["Aggregated", "GET attendance summary", "GET current sessions and roster"]:
            writer.writerow(dict(zip(fields, ["GET", name, 10, 0, latency, latency, latency])))
    (tmp_path / "perf-duration.json").write_text(
        json.dumps(
            {
                "login_successes": 100,
                "minimum_active_users_during_measured_period": 100,
                "measured_seconds_after_full_spawn": 600,
            }
        )
    )
    result = subprocess.run(
        [
            sys.executable,
            str(Path(__file__).resolve().parents[1] / "validation/summarize_load.py"),
            str(tmp_path),
            "perf",
            "--users",
            "100",
            "--seconds",
            "600",
        ],
        capture_output=True,
        text=True,
    )
    assessment = json.loads((tmp_path / "perf-assessment.json").read_text())
    assert assessment["passed"] is accepted
    assert (result.returncode == 0) is accepted
