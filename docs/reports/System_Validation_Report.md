# System validation report

Generated from actual execution at 2026-10-29T10:08:46.165802+00:00. Database: SQLite.

Chromium browser workflow results:

- Faculty login and role dashboard
- Faculty submits real class roll with P/A/OD controls
- Student sees own percentages
- Student creates correction request
- Faculty approval persists and notifies student
- Faculty downloads PDF and CSV reports
- Admin sees immutable correction history
- 360px mobile layout has no page overflow

JavaScript errors: 0.

Automated backend validation covers authentication, idle expiry, logout, reset, roles, ownership, marking, duplicate prevention, corrections, timetable validation, reporting, notification retries and append-only audit storage.

Pending deployment/UAT evidence: live TLS certificate verification, full-scale concurrent Locust run on staging, ZAP/Lighthouse audits, faculty sign-off, academic-year retention and semester uptime. These are not marked passed by unit tests. See `docs/TEST_PLAN_ADDENDUM.md`.
