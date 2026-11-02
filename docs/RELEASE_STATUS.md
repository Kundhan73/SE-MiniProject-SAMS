# Release status · 2 November 2026

The project has entered the teacher testing and closeout sprint (2–6 November 2026). Following final integration review, PR #1 was successfully merged into `main` (commit `c9e305f`) by repository owner Kundhan73, passing all GitHub Actions checks and triggering delivery publication to GHCR.

## Milestone progress and review

### 1. Integration and Delivery (PR #1)
- Merged to `main` at `c9e305f149970b3596ac7fd370c27f1c8e47f5ce`.
- Combined QA PR #48, admin/accessibility PR #50, and validation/evidence PR #53 with preserved history and attribution.
- Main CI passed; GitHub Container Registry image built and published.

### 2. Assigned Acceptance Retests and Target-Scale Latency (PR #54)
- Authored by DarkTJ7 (Tarun J) on branch `tarun/acceptance-20261102`.
- Addressed 300-user scale latency bottleneck:
  - Configured Gunicorn with `--worker-class gthread --threads 4` (2 workers, 4 threads/worker) to allow overlapping I/O while preserving CPU/memory limits (< 4 GiB).
  - Configured PostgreSQL connection pooling (`CONN_MAX_AGE=60`, `CONN_HEALTH_CHECKS=True`) in `sams/settings.py`.
  - Locust validation against application candidate `b60f42b`: 100 users p95 = 20 ms (600s), 300 users p95 = 60 ms (120s), 0 failures (target <= 3,000 ms fully satisfied).
- Published full evidence archive, case register (60 functional, 33 security, 12 auth boundary, 49 browser cases, 6 Lighthouse 100 audits), and rollback runbooks (`POSTGRES_CONN_MAX_AGE=0`, synchronous worker revert).
- **QA Code Review:** Reviewed and APPROVED by Anish (@planetai05) on 2 November 2026.

### 3. QA Monitoring Safeguards & Test Suite Expansion
- Expanded `tests/test_monitor.py` suite covering HTTP error responses, network connection failures, non-list history rejections, CLI summary/check-once flags, and calendar boundary checks.
- Statement coverage for `scripts/monitor_uptime.py` raised from 78.48% to 96.20%.
- Integrated backend test suite verified: **162 passing tests** (0 failures, 0 errors), **100.0% statement coverage** (764/764), and **98.24% branch coverage** (167/170).

## Remaining external actions and dependencies

| Owner | Remaining action |
| --- | --- |
| Tarun (DarkTJ7) | Personally review evidence and record scoped tester conclusion; confirm affected integration retests and required human/device observations. Assisted case execution alone is not his signature. |
| Owner (Kundhan73) | Merge PR #54 into `main` after teammate QA approval and verify post-merge main CI/delivery. |
| Owner / Faculty or IT | Supply a staging host/domain and external test email service if public TLS/internet delivery is required; otherwise obtain an explicit scope decision. |
| Team / Faculty | Complete live faculty demonstration (15 minutes), defense, and teacher UAT evaluation sign-off. |
| Operator / QA | Install/rehearse backup, recovery, encrypted offsite retention, and collect genuine multi-month semester uptime logs over time. |

Jira synchronization remains paused at the owner's request. GitHub is the current source of assignments and evidence. Board status follows reviewed evidence without inferring automated completion of real-world faculty sign-off.
