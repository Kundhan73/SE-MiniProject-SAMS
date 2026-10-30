# Tester handoff after developer integration

29 October 2026. Implementation PR: [#1](https://github.com/Kundhan73/SE-MiniProject-SAMS/pull/1). Developer: Kundhan73; Tester: DarkTJ7; QA: planetai05.

## Integrated changes

- [#45](https://github.com/Kundhan73/SE-MiniProject-SAMS/issues/45): an attendance PDF now renders a missing percentage as `No classes`; numeric percentages retain `%`.
- [#46](https://github.com/Kundhan73/SE-MiniProject-SAMS/issues/46): the System Validation Report separates current backend results from supplied browser/performance artifacts. It preserves artifact timestamps, shows missing provenance as unavailable, and states that report generation does not execute those tests.
- Three regression executions cover these changes. The code changes supplied in the local fix archive were reviewed, their failures reproduced before integration, and the integrated suite rerun by the developer.

Source: [Tarun's execution evidence](https://github.com/Kundhan73/SE-MiniProject-SAMS/pull/1#issuecomment-6497995970) and its attached archive, local fix commit `b8b2c098633b43ae58b116b2514ec15c56c3a86b` based on `824fb57ad44531bb6489b49e8c94af1112503aec`. That archive records Codex-assisted execution on Tarun's laptop; it is not a personal tester, QA or faculty sign-off. The original failures remain in the archive.

The latest GitHub Actions run on PR #1 is the source for hosted verification of the integrated commit. Developer checks do not close the independent testing tasks.

## Tarun: retest the integrated version

Preserve any local changes first, then update the implementation branch:

```bash
git fetch origin
git switch implementation/sams-ci-delivery
git pull --ff-only origin implementation/sams-ci-delivery
git rev-parse HEAD
```

Record the full resulting commit in the test results. Use the existing virtual environment with the requirements installed, then run:

```bash
python -m pytest --cov --cov-report=xml:docs/reports/coverage.xml --junitxml=docs/reports/junit.xml
python scripts/test_reports.py
```

The current suite has 138 test instances. Record actual counts rather than copying this expected count. Keep the environment, run time, command output, JUnit and coverage XML with the results.

1. Restart the local app from this branch using an isolated demo database.
2. Retest #45: create a course/section with an enrolled student but no submitted classes, export its PDF, and verify `No classes` without `%`. Also export a row with a numeric percentage and verify its `%` remains.
3. Retest #46: generate the reports without rerunning browser/load tests. Confirm the system report labels those artifacts separately, retains their available timestamps, reports unavailable source metadata honestly, and does not claim this command ran browser/load tests.
4. Attach the actual retest results to #45/#46 under DarkTJ7, with the integrated commit. Keep original failures and the new retests distinguishable. Request closure only once the integrated result has been verified and QA has assessed it.
5. Link the existing execution evidence and any new results to assigned issues #37–#42. Identify which acceptance scenarios are covered by each result and which are still untested. Do not rerun already sufficient cases merely to duplicate evidence; run gaps and regressions affected by changes.
6. Review the evidence personally and record an honest Tester conclusion. Assisted execution, personal review, QA approval and faculty UAT are separate records.

## Validation still pending

| Issue / area | Remaining work |
| --- | --- |
| #29 performance | Review the hosted PostgreSQL target-scale evidence and complete required staging validation; retain environment, dataset, concurrency and latency evidence. |
| #30 security | ZAP on an isolated staging environment, live TLS validation and any uncovered security scenarios. |
| #31 accessibility | Lighthouse, keyboard navigation, responsive checks and required cross-browser/accessibility coverage. |
| #42 notifications | Verify scheduled execution and external email delivery in an appropriate environment; distinguish these from directly invoking a task or console email. Check retry/dead-letter acceptance evidence. |

The local archive did not execute PostgreSQL/container/load, ZAP/TLS, full accessibility/cross-browser, external SMTP or scheduler timing. Existing CI evidence can be reviewed for the scenarios it actually covers; it is not evidence of a fresh execution on Tarun's laptop. If staging is unavailable, record the blocker and arrange it with the developer. Only faculty can grant a waiver of required external validation.

## Anish: QA handoff

Review the integrated diff, Tarun's retests, traceability and open defects. Give an actual PR review decision from planetai05. Kundhan merges only after required checks and peer review pass. Main CI and Delivery then need their own successful runs. Remaining submission/UAT and time-based operational requirements stay tracked in `SUBMISSION_CHECKLIST.md`.
