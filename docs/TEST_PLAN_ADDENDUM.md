# Test Plan execution addendum · 3 November 2026

This is the current execution update to the submitted IEEE-style Test Plan. The 89 original designed cases and baseline requirement IDs remain unchanged; current results are recorded here, in the revised PDF's execution supplement, the dated case register and actual generated reports. Original baseline Pending cells are historical design-time entries, not current execution claims.

The teacher's Parts 1–3 require updated cases, four reports under docs, assigned-member PRs and GitHub Actions. Part 2 explicitly permits GPT-assisted implementation. The current cycle is 2–6 November; the Test Plan excludes semester uptime from this test cycle (section 4).

## Environment and permitted staging scope

Python 3.12, Django 5.2 LTS, SQLite/PostgreSQL 16, Docker, Redis, Celery/Beat, Nginx and controlled Mailpit email capture. PostgreSQL/Mailpit replace the older version/MailHog names as documented deviations. The submitted Test Plan permits a self-signed staging certificate and captured test email (sections 6, 10 and 11). Private-CA localhost TLS and real Mailpit SMTP execution are valid evidence for that isolated scope; no additional public domain or Internet mailbox is required merely to pass those assignment tests. Neither result claims production hosting or Internet delivery.

## Executed evidence

| Area | Current evidence and actual result |
| --- | --- |
| Backend | 167 local test executions, zero failures; generated JUnit, coverage XML and four reports under docs/reports. CI independently executes both databases. Parametrized executions are not 167 unique original designed cases. |
| Coverage | 100% application statements, 98.24% branches. XML retains repository-relative, distinct module paths. Statement >=80% and branch >=70% gates enforced. |
| Functional/system | Tarun's 2 November register: 60 live functional cases, 33 authenticated security cases, 12 auth boundaries, 49 browser cases and six Lighthouse accessibility snapshots at 100. Each identifies its own source. |
| Performance | Candidate b60f42b: 100 clients for 600.03s, 35,018 requests, zero failures, p95 20ms; 300 clients for 120.04s, 62,968 requests, zero failures, p95 60ms. Aggregate includes ramp traffic; 300 clients reuse 100 faculty identities and make no new submissions. Actual deployment capacity remains environment-specific. |
| Notifications | Real accelerated Beat/worker execution: 2,002 daily Mailpit deliveries with no duplicate keys, 5/5 correction deliveries, four failed SMTP attempts and successful recovery. Production daily schedule unchanged. |
| Security/TLS | Nine verified private-CA localhost TLS cases and three bounded role-authenticated ZAP scans; no High/Medium alert in the retained final assessment. Low/informational findings and scan limits remain documented. |
| Jenkins/Sonar | Real Jenkinsfile execution retained in testing/jenkins-2026-11-03: 166 tests in that recorded run, dependency audit and Docker build successful; actual Sonar coverage condition 99.7% >=80%. Latest Actions identify subsequent execution of the added retention regression. |
| Retention | ST_OPS_01 creates dated synthetic audit rows across the academic year, runs the notification task, and verifies all remain queryable through the Admin date-range API. This proves tested retention/query behavior, not elapsed-year operation. |

## Updated cases and regressions

[TRACEABILITY.md](TRACEABILITY.md) maps requirement IDs to implementation/tests. [Tarun's case register](testing/tarun-2026-11-02/Case-Register.md) supplies expected/actual results, commits and evidence for live scenarios. [The current suite](reports/Unit_Test_Report.md) records every executed automated test. The revised PDF includes a generated execution register of case IDs explicitly named in current JUnit.

Regression additions cover PDF No classes formatting, report provenance, accessible form labels/keyboard tables, same-origin Swagger, database-health outage, monitor errors/history/CLI/calendar, strict 3,000ms rejection, repository-relative coverage paths and synthetic academic-year audit retention. Original failed results are retained, including scale bottlenecks and fixture setup failures.

## Remaining acceptance

Tarun must record the Test Plan's actual manual cross-testing/keyboard and iOS Safari/Android Chrome observations. Anish must finish the final revised-PDF/requirement mapping review and release checklist. Faculty and two student volunteers must actually perform/sign the stated UAT. These are human observations and cannot be replaced with invented testimony. No new screen-reader requirement is added by this reconciliation.

Semester uptime is an operational follow-up outside this cycle. A public production deployment needs a selected host/domain/mail service; it is not an extra prerequisite invented for the plan's permitted isolated staging tests. Signature/approval fields remain unfilled until the actual person approves.
