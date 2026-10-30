# SAMS: 15-minute demonstration outline

Review edition · 30 October 2026. This outline supports the team presentation; it is not a record of a presentation already delivered. Use synthetic demo data and the actual reviewed commit.

| Time | Presenter | Content |
| --- | --- | --- |
| 0:00–1:00 | Kundhan | Explain the attendance problem, scope and three project roles. |
| 1:00–3:00 | Anish | Show the revised SRS/SAD/Test Plan, one requirement traced to implementation and tests, and documented deviations. Distinguish completed preparation from the planned 2–6 November window. |
| 3:00–8:00 | Kundhan | Demonstrate the Student, Faculty and Admin flows below. |
| 8:00–10:00 | Tarun | Show actual cases, original defects/retests, the newest integrated test/coverage reports and GitHub Actions results. State the tested commit and assisted/human scope accurately. |
| 10:00–12:00 | Tarun | Explain browser/accessibility/security evidence and its limits; compare the supplied passing 100-client run with the failing 300-client latency result. |
| 12:00–14:00 | Anish | Review maintenance procedures, deployment/monitoring tasks still pending and the final acceptance checklist. Show actual PR review history and distinguish earlier approval from final approval. |
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

- Final integrated PR and newest CI run, including both database jobs.
- docs/reports/summary.json and the four generated reports; read current values instead of reusing older branch counts.
- docs/testing/tarun-2026-10-29/README.md and docs/testing/tarun-2026-10-30/README.md, including limitations and original failures.
- docs/TRACEABILITY.md, docs/MAINTENANCE_PLAN.md and docs/SUBMISSION_CHECKLIST.md.
- Existing one-minute retrospective and two-minute working-product recordings. Their actual recording dates remain visible.

## Statements that require evidence

The supplied normal profile measured 100 clients for 600 seconds, zero failures and aggregate p95 150 ms on baseline 05ce028. The 300-client profile measured aggregate p95 3,100 ms and failed its latency criterion. Do not describe either as a fresh integrated test or public staging capacity. The aggregate includes ramp traffic.

Mailpit captures local SMTP. Localhost private-CA TLS verifies that isolated endpoint, not public hosting. Automated browser/axe/Lighthouse checks do not establish physical-device or human screen-reader acceptance.

Backup/restore/rollback commands are documented procedures. Automated encrypted backups, offsite storage, external alerts, recovery objectives and semester uptime remain unverified until actually configured and measured. Rollback is not guaranteed to be instantaneous, zero-downtime or zero-data-loss.

The owner's merge follows genuine final peer review and green protected checks. A demonstration of passing automation is not a personal teammate signature or faculty UAT.
