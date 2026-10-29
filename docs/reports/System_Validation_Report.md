# System validation report

Generated from actual execution at 2026-10-29T09:51:49.970079+00:00. Database: SQLite.

Browser execution evidence is supplied separately by the Browser workflows CI job. This local report does not assert that browser tests ran.

Automated backend validation covers authentication, idle expiry, logout, reset, roles, ownership, marking, duplicate prevention, corrections, timetable validation, reporting, notification retries and append-only audit storage.

Pending deployment/UAT evidence: live TLS certificate verification, full-scale concurrent Locust run on staging, ZAP/Lighthouse audits, faculty sign-off, academic-year retention and semester uptime. These are not marked passed by unit tests. See `docs/TEST_PLAN_ADDENDUM.md`.
