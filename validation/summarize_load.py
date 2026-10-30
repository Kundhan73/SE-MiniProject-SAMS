"""Assess actual traffic and duration; retain failures rather than treating exit 0 as pass."""

import argparse
import csv
import json
import os
from pathlib import Path

parser = argparse.ArgumentParser()
parser.add_argument("directory", type=Path)
parser.add_argument("profile")
parser.add_argument("--users", type=int, required=True)
parser.add_argument("--seconds", type=int, required=True)
parser.add_argument("--require-marking", action="store_true")
args = parser.parse_args()
rows = list(csv.DictReader((args.directory / (args.profile + "_stats.csv")).open()))
aggregate = next(row for row in rows if row["Name"] == "Aggregated")
duration = json.loads((args.directory / (args.profile + "-duration.json")).read_text())
names = {row["Name"] for row in rows if int(row.get("Request Count") or 0) > 0}
complete = (
    duration.get("login_successes") == args.users
    and duration.get("minimum_active_users_during_measured_period", 0) >= args.users
    and duration.get("measured_seconds_after_full_spawn", 0) >= args.seconds
    and {"GET attendance summary", "GET current sessions and roster"} <= names
)
if args.require_marking:
    complete = complete and duration.get("mark_successes", 0) > 0
result = {
    "source_commit": os.getenv("SAMS_SOURCE_SHA", "05ce0282959ab2084b553bcd1e43aa312961d21c"),
    "profile": args.profile,
    "expected_users": args.users,
    "minimum_seconds_after_full_spawn": args.seconds,
    "duration": duration,
    "requests": int(aggregate["Request Count"]),
    "failures": int(aggregate["Failure Count"]),
    "p95_ms": float(aggregate["95%"]),
    "workload_complete": complete,
    "latency_target_met": float(aggregate["95%"]) <= 3000,
    "per_endpoint": [
        {
            key: row[key]
            for key in [
                "Type",
                "Name",
                "Request Count",
                "Failure Count",
                "95%",
                "Average Response Time",
                "Max Response Time",
            ]
        }
        for row in rows
        if row["Name"] != "Aggregated"
    ],
    "scope": "Isolated Linux Docker acceptance stack; app+database+proxy+Redis share two logical CPUs; configured memory budget below 4 GiB. Ramp 0.5 users/s preserves the production anonymous login rate limit. All ramp/login requests remain included in statistics; passwords use production hashing.",
}
result["passed"] = bool(complete and result["failures"] == 0 and result["latency_target_met"])
result["status"] = "PASS" if result["passed"] else "FAIL"
if args.users == 300 and complete and result["failures"] == 0 and not result["latency_target_met"]:
    result["status"] = "BOTTLENECK_REQUIRES_ASSESSMENT"
(args.directory / (args.profile + "-assessment.json")).write_text(json.dumps(result, indent=2))
print(json.dumps(result, indent=2))
assert result["passed"], "Acceptance criteria were not met; evidence retained."
