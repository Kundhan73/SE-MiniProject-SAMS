"""Generate the four requested reports from fresh JUnit and coverage data."""

import json
import os
from pathlib import Path
from datetime import datetime, timezone
from xml.etree import ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "docs/reports"


def main():
    junit = ET.parse(OUT / "junit.xml").getroot()
    tests = junit.findall(".//testcase")
    failed = [t for t in tests if t.find("failure") is not None or t.find("error") is not None]
    coverage = ET.parse(OUT / "coverage.xml").getroot()
    lines = int(coverage.attrib["lines-valid"])
    hit = int(coverage.attrib["lines-covered"])
    branches = int(coverage.attrib["branches-valid"])
    covered = int(coverage.attrib["branches-covered"])
    stamp = datetime.now(timezone.utc).isoformat()
    database = "PostgreSQL" if os.getenv("POSTGRES_HOST") else "SQLite"
    summary = {
        "generated_at": stamp,
        "database": database,
        "tests": len(tests),
        "failures": len(failed),
        "line_percent": round(hit / lines * 100, 2),
        "branch_percent": round(covered / branches * 100, 2),
    }
    (OUT / "summary.json").write_text(json.dumps(summary, indent=2) + "\n")
    header = f"Generated from actual execution at {stamp}. Database: {database}.\n\n"
    (OUT / "Unit_Test_Report.md").write_text(
        "# Unit and integration test report\n\n"
        + header
        + f"Executed: {len(tests)} automated test instances. Failed/error: {len(failed)}.\n\nThe suite includes service-level tests and real API/database integration tests; parametrized cases count as separate executions. Source: `junit.xml`. Test IDs map to the revised Test Plan addendum.\n\n"
        + "| Automated case | Result |\n| --- | --- |\n"
        + "\n".join(f"| {t.attrib['name']} | {'FAIL' if t in failed else 'PASS'} |" for t in tests)
        + "\n"
    )
    (OUT / "Code_Coverage_Report.md").write_text(
        "# Code coverage report\n\n"
        + header
        + f"Statements covered: **{hit}/{lines} ({hit / lines * 100:.2f}%)**. Target: 80%.\n\nMeasured application modules: accounts, attendance, audit, core, courses, notifications and reports. Migrations, management commands and framework internals are excluded. This percentage does not measure frontend JavaScript, deployment configuration, security assurance, or user acceptance. Raw evidence: `coverage.xml`; CI also uploads the HTML coverage report.\n"
    )
    (OUT / "Branch_Coverage_Report.md").write_text(
        "# Branch coverage report\n\n"
        + header
        + f"Branches covered: **{covered}/{branches} ({covered / branches * 100:.2f}%)**. Target: 70%.\n\nBranches are measured by coverage.py with branch measurement enabled. Each observed control-flow destination counts as a branch. Source: `coverage.xml`.\n"
    )
    system = (
        "# System validation report\n\n"
        + f"Report generated at {stamp}. Current backend database: {database}.\n\n"
        + f"Current backend execution: {len(tests)} test instances, {len(failed)} failures/errors, "
        + f"{summary['line_percent']}% statement coverage and {summary['branch_percent']}% branch coverage. "
        + "Sources: `junit.xml` and `coverage.xml`. Report generation does not execute tests.\n\n"
    )
    browser = OUT / "browser-results.json"
    if browser.exists():
        result = json.loads(browser.read_text())
        system += (
            "## Separately supplied browser evidence\n\n"
            "This artifact was not rerun by this report command; it is not counted as current local execution.\n\n"
            + f"Browser execution timestamp: {result.get('generated_at', 'unavailable')}. "
            + f"Source commit: {result.get('source_commit', result.get('commit', 'unavailable'))}. "
            + "Source file: `browser-results.json`. Verify its provenance before using it as release evidence.\n\n"
            + "\n".join("- " + c for c in result["checks"])
            + "\n\nJavaScript errors: "
            + str(len(result["javascript_errors"]))
            + ".\n\n"
        )
    else:
        system += "Browser execution evidence is supplied separately by the Browser workflows CI job. This local report does not assert that browser tests ran.\n\n"
    performance = OUT / "performance.json"
    if performance.exists():
        perf = json.loads(performance.read_text())
        system += (
            "## Separately supplied performance evidence\n\n"
            "This artifact was not rerun by this report command; it is not counted as current local execution.\n\n"
            + f"Performance execution timestamp: {perf.get('generated_at', 'unavailable')}. "
            + f"Source commit: {perf.get('source_commit', perf.get('commit', 'unavailable'))}. "
            + "Source file: `performance.json`.\n\n"
            + f"Reported load test: {perf['dataset_students']} students, {perf['dataset_faculty']} faculty, {perf['concurrent_users']} concurrent users, {perf['requests']} requests, {perf['failures']} failures, p95 {perf['p95_ms']} ms. "
            + f"Artifact scope: {perf.get('scope', 'unavailable')}. "
            + "This is not a semester uptime or production-capacity guarantee.\n\n"
        )
    system += "Automated backend validation covers authentication, idle expiry, logout, reset, roles, ownership, marking, duplicate prevention, corrections, timetable validation, reporting, notification retries and append-only audit storage.\n\nPending deployment/UAT evidence: live TLS certificate verification, full-scale concurrent Locust run on staging, ZAP/Lighthouse audits, faculty sign-off, academic-year retention and semester uptime. These are not marked passed by unit tests. See `docs/TEST_PLAN_ADDENDUM.md`.\n"
    (OUT / "System_Validation_Report.md").write_text(system)
    print(json.dumps(summary, indent=2))
    if failed or hit / lines < 0.8 or covered / branches < 0.7:
        raise SystemExit("Test/coverage gate failed")


if __name__ == "__main__":
    main()
