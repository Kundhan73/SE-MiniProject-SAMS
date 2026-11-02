# Current team handoff · 3 November 2026

Tarun's technical retests and performance tuning are merged in [PR #54](https://github.com/Kundhan73/SE-MiniProject-SAMS/pull/54). Anish's monitoring regressions and submission updates are combined with developer corrections in [PR #56](https://github.com/Kundhan73/SE-MiniProject-SAMS/pull/56). Use `main` after integration and read its latest Actions results before presenting.

Preserve local changes, then update:

```bash
git fetch origin
git switch main
git pull --ff-only origin main
git rev-parse HEAD
```

The developer's combined local run passed 167 test instances, with 100% application statement coverage and 98.24% branch coverage. Actual counts and environment are in [the generated reports](reports/summary.json); historical branch counts are not current expectations. Both databases, browser acceptance and the real Jenkins/Sonar pipeline are checked in Actions. Review their actual conclusions rather than inferring success from configuration.

| Member | Remaining team action |
| --- | --- |
| Kundhan — Developer | Verify final main CI, Jenkins/Sonar and image delivery; run the synthetic-data demo from main. Configure the selected server/domain/mail service if the evaluator requires public deployment. |
| Tarun — Tester | Review the dated case register, confirm the independent observations required by the course, and demonstrate the actual results. Record the Test Plan's manual cross-testing/keyboard and actual iOS Safari/Android Chrome observations. No repeat of already sufficient automated cases is needed solely to duplicate evidence. |
| Anish — QA | Review the final revised SRS/SAD/Test Plan mapping and release checklist, confirm remaining gaps, and prepare the report/presentation for faculty evaluation. His actual PR #54 approval is recorded; no approval of later revisions is invented. |
| All three | Rehearse and deliver the 15-minute presentation, product walkthrough and defense. Faculty UAT and semester observations require their actual participants/time. |

[Tarun's 2 November report](testing/tarun-2026-11-02/README.md) retains 60 functional, 33 security, 12 auth-boundary, nine localhost TLS and 49 browser cases, scheduled Mailpit delivery/recovery, and the full load comparison. Original failed executions remain available. The final tuning candidate measured p95 20 ms at 100 clients and 60 ms at 300 clients with zero failures. These are isolated measurements; aggregate latency includes ramp traffic and 300 clients reuse 100 faculty identities without new attendance submissions.

The executed technical tasks #29 and #37–#42 are closed with evidence. The Test Plan explicitly permits captured email and self-signed staging TLS, so Mailpit/private-CA checks are valid for that scope. Public hosting and Internet email are separate production work. Actual mobile browsers/manual cross-testing remain distinct from emulation, and semester uptime is excluded from this test cycle. Personal testimony, faculty approval and a scope waiver must come from the people concerned.

See [release status](RELEASE_STATUS.md), [submission checklist](SUBMISSION_CHECKLIST.md), [traceability](TRACEABILITY.md) and the dated [29 October](testing/tarun-2026-10-29/README.md)/[30 October](testing/tarun-2026-10-30/README.md) evidence.
