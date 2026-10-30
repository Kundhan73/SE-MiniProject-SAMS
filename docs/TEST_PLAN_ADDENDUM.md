# Test Plan addendum · 29 October 2026

This document updates the submitted IEEE-style STP alongside the revised PDF. Scope and requirement IDs remain those of the original SRS. The teacher's Part 3 testing window is **2–6 November 2026**; development and preparation checks are being executed earlier.

## Test items, features and exclusions

Test items are the accounts, courses, attendance, reports, notifications, audit and core/API modules plus the three role dashboards. Functional, error, authorization, boundary and regression scenarios are implemented in `tests/test_domain.py`, `tests/test_api.py` and `tests/test_workflows.py`.

External ERP, biometric hardware, fees and grading remain excluded. Semester uptime, academic-year retention and human UAT cannot be demonstrated by an instantaneous automated run. The baseline 89 designed case IDs remain the baseline: automated test names reference relevant IDs; parametrized executions increase the execution count but are not represented as 89 original cases all individually signed off.

## Approach and environment

Python 3.12, Django 5.2 LTS, DRF, pytest and coverage.py. SQLite runs fast service/API regression tests; the same suite also runs on PostgreSQL 16 in GitHub Actions. Tests use an isolated database and synthetic identities. Email is captured by a memory backend; SMTP failure behavior is tested with controlled transport failures. Production password hashing is verified separately from the deliberately fast test-only hasher.

All PRs run lint, formatting, migration drift detection, tests, statement/branch measurement, dependency audit, browser workflows and container build/health checks. Required coverage: statements >=80%, branches >=70%. The report generator fails if either threshold is unmet. Reports are generated from actual JUnit and coverage XML, not handwritten counts.

Browser checks use real Chromium login, marking, student correction, faculty approval, export downloads, administrator audit display and a 360px layout check. These establish core flows in Chromium; they do not constitute a complete cross-browser WCAG audit.

## Security validation (STP 5.1 update)

| Area | Automated evidence | Additional validation |
| --- | --- | --- |
| Credentials and lockout | Valid/invalid login, fifth failure lockout, expiry, no tokens on failure | Review production hash configuration |
| Session handling | Expired access/idle session rejected; API and native logout revoke JWT family | Shared-device manual walkthrough |
| Reset | Hashed token, 30-minute expiry, single use, password policy, no enumeration in normal flow | Real SMTP delivery on staging |
| RBAC/ownership | Students rejected from faculty/admin APIs; other faculty/record access denied | Cross-role exploratory test |
| CSRF/input | Login CSRF rejection, native form CSRF, malformed JSON, invalid statuses, CSV formula neutralization | ZAP baseline/API scan on isolated staging |
| Audit | ORM and raw SQL mutation rejected; initial/edit/approved correction entries verified | Database permissions and backup review |
| Dependencies | pip-audit JSON, failed build on findings | Review new alerts before freeze |
| TLS | Production settings and TLS Nginx configuration | Live certificate/TLS/HSTS check after staging is provisioned |

## Representative cases and expected outcomes

| Case | Steps / boundary | Expected |
| --- | --- | --- |
| IT_AUTH_01 | Login each valid role | Correct role and authenticated access |
| UT_AUTH_03/04 | Five bad passwords, then correct password; expire lock | Locked until 15 minutes pass; then succeeds |
| IT_AUTH_04 + logout regression | Login via API, logout via cookie/API or web form, reuse tokens | Access and refresh both rejected |
| UT_PWR_02/03/04 | Expired/reused reset; weak password | Expired/reused rejected; weak password does not consume token |
| IT_AUTH_02 / ST_SEC_04 | Student calls admin, faculty marking and report APIs | 403 with no mutation/data disclosure |
| UT_ATT_03–06 | Mark P/A/OD; retry; invalid status; incomplete/foreign roster | One atomic save; duplicate 409; invalid inputs write nothing |
| Submitted-roster regression | Submit, enroll another student, reopen | Only actual saved marks appear in the submitted roster |
| UT_ATT_07 | Faculty explicitly edits with reason | New value plus editor/old/new/time/reason audit |
| UT_COR_01–06 | Own correction, duplicate, other student's record, approve/reject/re-decide | Routed to correct faculty; one pending request; atomic decision and audit |
| UT_VIEW / UT_REP | OD, no classes, threshold equality, date-range boundaries | OD counts; no-class percent null; strictly below threshold; inclusive dates |
| UT_CRS_02–05 | Invalid/clashing/adjacent slots, partially invalid CSV | Invalid/clashing rejected; adjacent accepted; valid rows enrolled with row errors |
| UT_NOT_01–04 | Repeat daily scan, SMTP failure, retry | No duplicate daily alert; in-app persisted; failed email observable |
| UT_ADM_03/04 | Audit update/delete via API, ORM and SQL | API read-only; storage rejects mutation |
| Browser smoke | Three-role flow plus downloads and mobile width | Persisted results, valid downloads, no JS errors/page overflow |

## Execution, reporting and exit criteria

Run commands in the README. `scripts/test_reports.py` writes the four requested reports under `docs/reports/`; raw evidence is retained alongside them. CI uploads separate database reports and browser evidence. Consult each artifact's timestamp and commit rather than assuming an earlier report covers newer changes.

Before freeze: all mandatory automated checks pass, no unresolved critical/high bugs, peer review completed, every FR traced, and remaining external checks either executed or explicitly waived by faculty. The actual CI target-scale load evidence is in `docs/reports/performance.json` (PostgreSQL; 2,000 students, 100 faculty; 20 concurrent users). Staging capacity confirmation, UAT, complete accessibility, ZAP/TLS and semester uptime remain **pending until actually performed**. No human approval is inferred from an automated pass.

## Current test responsibilities

Kundhan (Developer) implements features and fixes and provides automated regression tests with code changes. Tarun (Tester) owns independent execution of UC-01 through UC-09 plus security, accessibility and performance scenarios, records actual results and retests fixes. Anish (QA) reviews the plan, checks requirement-to-evidence coverage, audits reports and assesses release readiness. Test execution, QA review and faculty UAT are separate sign-offs; none is inferred from assigning a task.

## Defects from the 29 October local test session

Issues #45 (PDF `No classes%`) and #46 (report evidence provenance) were reproduced against `824fb57ad44531bb6489b49e8c94af1112503aec`. Both failing regressions were reproduced again during developer integration before applying the supplied fixes. `tests/test_validation_regressions.py` adds three executions: missing percentage, numeric percentage, and separation of current backend results from supplied browser/performance artifacts.

Tarun's attached archive records Codex-assisted execution on his Windows/SQLite/Opera environment, including targeted local retests; it does not assert a personal tester, QA or faculty sign-off. The integrated branch requires a new independent retest against its actual GitHub commit. The [tester handoff](TESTER_HANDOFF.md) gives the steps and identifies remaining validation.
