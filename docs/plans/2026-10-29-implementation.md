# SAMS implementation and delivery plan

Goal: implement the submitted SAMS requirements and the teacher's three deliverable sheets.

Approach: retain the Django/DRF modular monolith and original PDFs; add working code, migrations, role dashboards and repeatable verification. GitHub Actions is the primary hosted CI, with Jenkins and SonarQube support retained from the design. Use SQLite for a quick local demo and PostgreSQL/Redis/Celery/Nginx in Docker.

1. Build accounts, courses, attendance, reports, notifications and audit modules. Services own business rules; endpoints enforce roles and ownership.
2. Add regression tests for lockout/reset, atomic attendance, correction decisions, report boundaries, timetable clashes, permissions and audit immutability.
3. Add responsive role dashboards and verify real login, marking and correction flows.
4. Add CI (lint, migration check, SQLite/PostgreSQL tests, coverage, dependency audit, Docker smoke test) and delivery (tested image publication).
5. Update test cases, traceability, deviations, deployment and demo instructions; generate reports from actual executions.
6. Create pointed GitHub backlog items and teacher-aligned sprints, open a PR, inspect hosted checks. Keep team review, video recordings, live TLS, uptime and UAT explicitly pending when evidence is unavailable.

Verification commands: `python manage.py check`, `python manage.py makemigrations --check --dry-run`, `ruff check .`, `pytest --cov --cov-report=term-missing --cov-report=xml:docs/reports/coverage.xml --junitxml=docs/reports/junit.xml`, `python scripts/test_reports.py`.
