# Submission checklist · 2 November 2026

## Part 1

- [x] SRS, architecture/design and test-plan PDFs updated for the current team and present in docs.
- [x] UML diagram sources and renders preserved.
- [x] Implementation/test-plan addenda and complete requirement traceability added.
- [ ] Faculty/team review of original document correctness and approvals.

## Part 2

- [x] Runnable Django product with Student, Faculty and Admin flows.
- [x] GitHub Actions CI and gated image delivery workflow implemented.
- [x] Pointed GitHub issues with acceptance context, original Jira links and teacher-aligned milestones.
- [x] Verified GitHub accounts assigned: Kundhan73, DarkTJ7 (Tarun J), planetai05 (Anish).
- [x] Linked GitHub Project board with estimates, sprint fields, assignees and team-role fields.
- [x] Current three-member team assigned by role: Developer Kundhan73, Tester DarkTJ7, QA planetai05.
- [x] Owner merge of PR #1 executed after green checks (`c9e305f`) using the authorized administrator override; the earlier teammate review was dismissed.
- [x] Actual working-product recordings: one-minute Sprint 1 retrospective and two-minute Sprint 2 demo in docs/demos. Recorded on 29 October, using synthetic data; silent browser demonstrations.
- [x] Deviations from earlier SRS/SAD/STP documented.
- [ ] Development freeze after review and required external validation or an explicit faculty scope decision.

## Part 3

- [x] Regression cases updated for implemented behavior and discovered bugs.
- [x] Report generation for Unit, System Validation, Code Coverage and Branch Coverage; actual results under docs/reports (166 tests passing, 100% statement coverage, 98.24% branch coverage).
- [x] Product Maintenance Plan (`docs/MAINTENANCE_PLAN.md`) and working-hours uptime monitoring utility (`scripts/monitor_uptime.py`).
- [x] Final Academic Project Report in Jackfruit format (`docs/FINAL_PROJECT_REPORT.md`).
- [x] 15-Minute Demo Presentation Deck & Delivery Guide (`docs/DEMO_PRESENTATION.md`).
- [ ] Complete live faculty demonstration, defense, and teacher UAT during 2–6 November evaluation.
- [ ] Record actual Jenkins/SonarQube results if the teacher requires those tools specifically, rather than GitHub Actions CI.
- [ ] Preserve semester uptime and academic-year retention evidence over time.

Unchecked items are not represented as completed merely because configuration or a test script exists. See current Actions run and timestamps in reports for executed evidence.

## 2 November testing sprint and review

- [x] Owner merge of PR #1 into `main` verified (`c9e305f`), triggering GHCR release image publication.
- [x] PR #54 opened by DarkTJ7 addressing 300-user scale latency via Gunicorn `gthread` concurrency and PostgreSQL persistent connections (`CONN_MAX_AGE=60`), achieving p95 20 ms at 100 users and 60 ms at 300 users (0 errors).
- [x] Independent QA Code Review & Architecture Verification of PR #54 conducted and APPROVED by Anish (@planetai05).
- [x] QA monitoring test suite expanded in `tests/test_monitor.py` covering error conditions, network failures, non-list history and CLI modes (separate monitor coverage measurement retained).
- [ ] Obtain Tarun's personal conclusion/signature under DarkTJ7.
- [ ] Complete public staging/external email and required human/device checks, or record the evaluator's explicit scope decision.

See [release status](RELEASE_STATUS.md) for the current handoff and [final report](FINAL_PROJECT_REPORT.md) for evidence scope.
