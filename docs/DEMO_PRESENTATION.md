# SAMS: 15-minute demonstration outline

Review edition · 3 November 2026. This outline supports the team presentation; it is not a record of a presentation already delivered. Use synthetic demo data and the actual reviewed commit.

| Time | Presenter | Content |
| --- | --- | --- |
| 0:00–1:00 | Kundhan | Explain the attendance problem, scope and three project roles. |
| 1:00–3:00 | Anish | Show the revised SRS/SAD/Test Plan, one requirement traced to implementation and tests, and documented deviations. Distinguish completed preparation from the scheduled 2–6 November evaluation. |
| 3:00–8:00 | Kundhan | Demonstrate the Student, Faculty and Admin flows below. |
| 8:00–10:00 | Tarun | Show actual cases, original defects/retests, the newest integrated test/coverage reports (167 tests, 100% statement, 98.24% branch coverage) and GitHub Actions results. State the tested commit and assisted/human scope accurately. |
| 10:00–12:00 | Tarun | Explain browser/accessibility/security evidence and its limits; explain how the 300-client scale bottleneck was diagnosed, tuned via Gunicorn gthread and PostgreSQL persistent connections, and resolved in PR #54 (p95 20 ms at 100 clients, 60 ms at 300 clients). |
| 12:00–14:00 | Anish | Review maintenance procedures, deployment/monitoring tasks still pending and the final acceptance checklist. Show actual PR review history (PR #1 merged by owner, PR #54 approved by Anish). |
| 14:00–15:00 | All | Questions, current limitations and next steps. |

## Product walkthrough

1. Start a fresh isolated demo using README instructions. Record the commit before presenting; never seed over an existing database.
2. Faculty signs in and submits P/A/OD for today's class. Show persisted marks and the duplicate-submission guard.
3. Student signs in, checks private percentages and requests a correction with a reason.
4. Faculty approves or rejects; show the updated state and notification.
5. Export a filtered CSV/PDF, including the No classes boundary if time permits.
6. Admin shows setup, correctly labelled controls, threshold and append-only audit history.
7. Show keyboard scrolling of a wide table at 360 px and the working same-origin Swagger documentation.

## Evidence to open in advance

- Final integrated PR #1 and PR #54 with CI runs, including both database jobs.
- docs/reports/summary.json and the four generated reports (167 tests, 100% statement coverage, 98.24% branch coverage).
- docs/testing/tarun-2026-10-29/README.md, docs/testing/tarun-2026-10-30/README.md, and docs/testing/tarun-2026-11-02/README.md.
- docs/TRACEABILITY.md, docs/MAINTENANCE_PLAN.md and docs/SUBMISSION_CHECKLIST.md.
- Existing one-minute retrospective and two-minute working-product recordings. Their actual recording dates remain visible.

## Statements that require evidence

Baseline runs showed normal 100-client load passed (p95 150 ms) while 300-client scale load queued (p95 3,100 ms – 3,800 ms). PR #54 resolved this with Gunicorn gthread workers (4 threads/process) and PostgreSQL connection reuse (60s), achieving p95 20 ms at 100 users and 60 ms at 300 users. Do not describe either as a public staging deployment.

Mailpit captures local SMTP. Localhost private-CA TLS verifies that isolated endpoint, not public hosting. Automated browser/axe/Lighthouse checks do not establish the Test Plan's actual iOS Safari/Android Chrome observations and manual cross-testing.

Backup/restore/rollback commands are documented procedures. Automated encrypted backups, offsite storage, external alerts, recovery objectives and semester uptime remain unverified until actually configured and measured. Rollback is not guaranteed to be instantaneous, zero-downtime or zero-data-loss.

PR #1 was merged to `main` and PR #54 was reviewed and approved by QA Engineer Anish (@planetai05). A demonstration of passing automation is not a personal teammate signature or faculty UAT.

Performance scope: aggregate p95 includes ramp/login traffic. The 300-client profile reuses 100 faculty identities and makes no attendance submissions; the 100-client profile includes 40 submissions. One full run of the final tuning candidate is recorded; deployment capacity requires revalidation.
