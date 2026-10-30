# Submission checklist · 29 October 2026

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
- [ ] Another team member's actual review of PR #1 and owner merge after green checks.
- [x] Actual working-product recordings: one-minute Sprint 1 retrospective and two-minute Sprint 2 demo in docs/demos. Recorded on 29 October, using synthetic data; silent browser demonstrations.
- [x] Deviations from earlier SRS/SAD/STP documented.
- [ ] Development freeze after review and required external validation.

## Part 3

- [x] Regression cases updated for implemented behavior and discovered bugs.
- [x] Report generation for Unit, System Validation, Code Coverage and Branch Coverage; actual results under docs/reports.
- [x] Product Maintenance Plan (`docs/MAINTENANCE_PLAN.md`) and working-hours uptime monitoring utility (`scripts/monitor_uptime.py`).
- [x] Final Academic Project Report in Jackfruit format (`docs/FINAL_PROJECT_REPORT.md`).
- [x] 15-Minute Demo Presentation Deck & Delivery Guide (`docs/DEMO_PRESENTATION.md`).
- [ ] Complete staging load, ZAP, Lighthouse, live TLS and UAT during 2–6 November (or record an explicit faculty waiver).
- [ ] Record actual Jenkins/SonarQube results if the teacher requires those tools specifically, rather than GitHub Actions CI.
- [ ] Preserve semester uptime and academic-year retention evidence over time.

Unchecked items are not represented as completed merely because configuration or a test script exists. See current Actions run and timestamps in reports for executed evidence.

## 30 October integration review

- [x] Combine QA PR #48, application/browser fixes PR #50 and archived validation/tooling PR #53, preserving their history and evidence.
- [x] Correct the final report/demo claims and monitoring false-positive/history/CLI issues found during integration review.
- [x] Strengthen browser acceptance to reject failed API/application screens and include a mocked-500 negative control.
- [ ] Obtain Tarun's actual personal conclusion and Anish's review of the final integrated commit; earlier approval at 05ce028 does not cover these additions.
- [ ] Resolve or obtain an explicit faculty assessment of the supplied 300-user latency miss; distinguish ramp-inclusive aggregate from sustained-only latency.
- [ ] Complete public staging/external email and required human/device checks, or record the evaluator's explicit scope decision.

See [release status](RELEASE_STATUS.md) for the current handoff and [final report](FINAL_PROJECT_REPORT.md) for evidence scope. The 2–6 November testing window remains future work as of this review date.
