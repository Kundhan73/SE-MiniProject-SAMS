# System validation report

Report generated at 2026-10-30T17:05:12.912476+00:00. Current backend database: SQLite.

Current backend execution: 154 test instances, 0 failures/errors, 100.0% statement coverage and 98.24% branch coverage. Sources: `junit.xml` and `coverage.xml`. Report generation does not execute tests.

## Separately supplied browser evidence

This artifact was not rerun by this report command; it is not counted as current local execution.

Browser execution timestamp: unavailable. Source commit: unavailable. Source file: `browser-results.json`. Verify its provenance before using it as release evidence.

- Faculty login and role dashboard
- Faculty submits real class roll with P/A/OD controls
- Student sees own percentages
- Student creates correction request
- Faculty approval persists and notifies student
- Faculty downloads PDF and CSV reports
- Admin sees immutable correction history
- 360px mobile layout has no page overflow

JavaScript errors: 0.

## Separately supplied performance evidence

This artifact was not rerun by this report command; it is not counted as current local execution.

Performance execution timestamp: 2026-10-29T10:06:59.709333+00:00. Source commit: unavailable. Source file: `performance.json`.

Reported load test: 2000 students, 100 faculty, 20 concurrent users, 393 requests, 0 failures, p95 1400.0 ms. Artifact scope: GitHub-hosted runner, PostgreSQL, 20 concurrent faculty sessions and reports; not a semester uptime or production capacity guarantee.. This is not a semester uptime or production-capacity guarantee.

Automated backend validation covers authentication, idle expiry, logout, reset, roles, ownership, marking, duplicate prevention, corrections, timetable validation, reporting, notification retries and append-only audit storage.

Pending deployment/UAT evidence: live TLS certificate verification, full-scale concurrent Locust run on staging, ZAP/Lighthouse audits, faculty sign-off, academic-year retention and semester uptime. These are not marked passed by unit tests. See `docs/TEST_PLAN_ADDENDUM.md`.
