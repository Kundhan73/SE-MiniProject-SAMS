# Release status · 3 November 2026

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
  - Configured PostgreSQL persistent connections (`CONN_MAX_AGE=60`, `CONN_HEALTH_CHECKS=True`) in `sams/settings.py`.
  - Locust validation against application candidate `b60f42b`: 100 users p95 = 20 ms (600s), 300 users p95 = 60 ms (120s), 0 failures (target < 3,000 ms fully satisfied).
- Published full evidence archive, case register (60 functional, 33 security, 12 auth boundary, 49 browser cases, 6 Lighthouse 100 audits), and rollback runbooks (`POSTGRES_CONN_MAX_AGE=0`, synchronous worker revert).
- **QA Code Review:** Reviewed and APPROVED by Anish (@planetai05) on 2 November 2026.

### 3. QA Monitoring Safeguards & Test Suite Expansion
- Expanded `tests/test_monitor.py` suite covering HTTP error responses, network connection failures, non-list history rejections, CLI summary/check-once flags, and calendar boundary checks.
- Monitor coverage is measured separately in `docs/reports/monitor-coverage.json`.
- Integrated backend test suite verified: **167 passing tests** (0 failures, 0 errors), **100.0% statement coverage** (764/764), and **98.24% branch coverage** (167/170).

## Remaining external actions and dependencies

| Owner | Remaining action |
| --- | --- |
| Tarun (DarkTJ7) | Record remaining manual cross-testing/keyboard and actual iOS Safari/Android Chrome observations from the Test Plan. Automated execution is complete within its recorded scope. |
| Owner (Kundhan73) | This revision combines merged PR #54, QA PR #55 and developer corrections through PR #56; check latest main CI/delivery. |
| Owner / Faculty or IT | A public host/domain and Internet mailbox are needed only for an actual public deployment. The submitted Test Plan permits self-signed staging certificates and captured test email. |
| Team / Faculty | Complete live faculty demonstration (15 minutes), defense, and teacher UAT evaluation sign-off. |
| Operator / QA | For ongoing operation, install/rehearse backup, recovery and monitoring. Semester uptime is explicitly outside this test cycle (Test Plan section 4). Synthetic historical audit rows verify academic-year query/retention logic separately. |

The owner requested a fresh one-time Jira reconciliation on 3 November. GitHub PRs, Actions and case registers supply the evidence; no continuous background sync is enabled. Board status follows reviewed evidence without inferring automated completion of real-world faculty sign-off.

## Developer closeout verification · 3 November

- PR #54 merged at `b69f49c`; this revision includes QA PR #55 and developer corrections through PR #56.
- Fresh integrated local suite: 167 passed, zero failures; 100% application statements and 98.24% branches.
- Coverage XML now retains distinct repository-relative application modules, including same-named files. The regression failed before the correction and passes afterward.
- The strict load gate rejects 3,000 ms, matching the under-three-second criterion; 2,999/3,000/3,001 ms boundaries are tested.
- The recorded Jenkins/Sonar run passed all stages, 166 tests and a measured 99.7% Sonar coverage condition against 80%. [Raw execution evidence](testing/jenkins-2026-11-03/README.md) identifies the tested source and preserved setup failures.
- Executed performance and functional test tasks #29/#37–#42 are closed with evidence. GitHub Project and Jira reflect these technical completions; remaining external/human/faculty observations remain open. Final main CI and Delivery are authoritative for the published revision.
