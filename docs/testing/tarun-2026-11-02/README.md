# Assigned-work validation — 2 November 2026

Application candidate: `b60f42b1ad29d488f4aa96e8f5964884764f6220`. Review: [PR #54](https://github.com/Kundhan73/SE-MiniProject-SAMS/pull/54), authored by **DarkTJ7**. All new commits use TARUN.J and the account's GitHub noreply address; no assistant co-author trailer or collaborator was added.

Execution is tool-assisted on Tarun's laptop and isolated GitHub Actions runners. This report does not claim Tarun personally performed the checks, independent QA approval, faculty UAT, a public staging deployment, or external mailbox delivery.

## What was already implemented

The teammate merged PR #1 into main at `c9e305f149970b3596ac7fd370c27f1c8e47f5ce`, including the earlier fixes and evidence from PRs #48/#50/#53. The old planetai05 review is dismissed. This work retests the integrated behavior and preserves earlier failures rather than attributing existing implementation to the tester.

## Changes proposed for review

The application keeps two Gunicorn processes and uses four request threads per process. PostgreSQL connections are reused for 60 seconds with health checks, reducing repeated connection setup. Authentication, production password hashing, anonymous rate limits, transaction locking and the CPU/memory budget are unchanged. `POSTGRES_CONN_MAX_AGE=0` rolls back connection reuse. Removing the gthread arguments rolls back request concurrency. See docs/DEPLOYMENT.md and the Django connection documentation linked there.

The validation harness records the actual application and tooling commits, retains real resource samples, and keeps baseline and candidate runs separate. A launch using an abbreviated commit failed before application checkout (run 41468900299); the complete SHA was supplied in run 41470374124. The workflow now validates full commit IDs before attempting checkout. This setup error is not an application test failure.

## Current verification

- Final local backend run: **154 passed**, 100% statement and 98.24% branch coverage. SQLite and PostgreSQL CI independently run the same 154-case suite; these are repeated executions, not 308 distinct cases.
- Live functional checks: **60/60 PASS** on `b60f42b`. Covers roles, CSRF, course/section setup, CSV imports, concurrent enrollment, timetable clashes, P/A/OD, duplicate/concurrent submissions, reasoned edits/audit, privacy, corrections, thresholds, parsed PDF/CSV, account suspension and session revocation.
- Authenticated security matrix: **33/33 PASS** on `b60f42b`. Includes RBAC/IDOR, injection probes, malformed input, credential-field exposure and JWT/session revocation.
- Additional live authentication boundaries: **12/12 PASS** on `b60f42b`. Five-failure lockout, uniform known/unknown reset requests, actual reset mail, weak-password rejection, token consumption/replay rejection, session revocation, old/new password and lockout recovery were exercised on a new synthetic account.
- Browser acceptance: **49 PASS**, plus **six Lighthouse accessibility snapshots at 100**. Actual checkout `c339794c7f7266c4c6c1e703fa43a534405c9bd9` is GitHub's temporary merge of the candidate into main. Physical devices and human assistive-technology use are not claimed.
- Local browser observation on `8b843a6`: stored script markup appeared as plain text (zero injected script/image elements); Tab/Enter completed a synthetic correction rejection and preserved its note. Screenshots record the actual local UI.

- Final browser observation on `b60f42b`: keyboard student login, student-only navigation, own attendance/no-class state without horizontal page overflow, and logout passed. The recovered retry email was also opened in Mailpit and captured in a screenshot.

## Performance measurements

SUT application, PostgreSQL, Redis and proxy share CPU set 0,1 with configured memory below 4 GiB; the load client uses separate cores 2,3. Dataset metadata and container budgets are retained in each run. The workload preserves production hashing/rate limits, uses 0.5 logins/second, and counts all ramp/login traffic. Normal load holds 100 clients for at least 600 seconds after full spawn and includes 40 real complete-roster submissions. Scale holds 300 clients for at least 120 seconds after full spawn, reusing 100 faculty identities. It does not claim 300 distinct users or 300 concurrent writes.

| Candidate | Profile | Actual commit | Requests | Failures | p95 ms | Full-client seconds | Result |
| --- | --- | --- | --- | --- | --- | --- | --- |
| [Merged main baseline](https://github.com/Kundhan73/SE-MiniProject-SAMS/actions/runs/41463066953) | perf100 | c9e305f | 33719 | 0 | 220.0 | 600.02 | PASS |
| [Merged main baseline](https://github.com/Kundhan73/SE-MiniProject-SAMS/actions/runs/41463066953) | perf300 | c9e305f | 31211 | 0 | 3800.0 | 120.06 | BOTTLENECK_REQUIRES_ASSESSMENT |
| [Threaded candidate](https://github.com/Kundhan73/SE-MiniProject-SAMS/actions/runs/41463388436) | perf100 | 8b843a6 | 34640 | 0 | 84.0 | 600.02 | PASS |
| [Threaded candidate](https://github.com/Kundhan73/SE-MiniProject-SAMS/actions/runs/41463388436) | perf300 | 8b843a6 | 43897 | 0 | 2900.0 | 120.04 | PASS |
| [Threaded repeat](https://github.com/Kundhan73/SE-MiniProject-SAMS/actions/runs/41468205742) | perf100 | 8b843a6 | 32680 | 0 | 380.0 | 600.04 | PASS |
| [Threaded repeat](https://github.com/Kundhan73/SE-MiniProject-SAMS/actions/runs/41468205742) | perf300 | 8b843a6 | 28548 | 0 | 6800.0 | 120.08 | BOTTLENECK_REQUIRES_ASSESSMENT |
| [Connection reuse](https://github.com/Kundhan73/SE-MiniProject-SAMS/actions/runs/41470374124) | perf100 | b60f42b | 35018 | 0 | 20.0 | 600.03 | PASS |
| [Connection reuse](https://github.com/Kundhan73/SE-MiniProject-SAMS/actions/runs/41470374124) | perf300 | b60f42b | 62968 | 0 | 60.0 | 120.04 | PASS |

The acceptance gate uses aggregate p95 strictly below 3000 ms. Endpoint distributions remain in each assessment: an aggregate pass does not imply every endpoint passed or that no individual response exceeded three seconds. These are isolated-run measurements, with runner variation and no production capacity or semester-uptime claim.

The thread-only candidate varied from 2,900 to 6,800 ms at scale and is not accepted as a reliable fix by itself. Connection reuse was evaluated as the second and final candidate. Its recorded p95s are 20 ms at 100 clients and 60 ms at 300 clients; the slowest recorded endpoint p95 at scale is faculty login at 370 ms. This is one complete run of that final candidate, with substantial headroom relative to both the criterion and observed earlier runner variation; revalidate on the actual deployment after merge.

## Scheduled notifications and recovery

Temporary 15-second beat scheduling exercised the real nightly task against the synthetic database. It produced **2002** daily notifications, **2002** successful Mailpit deliveries, **0** stored errors, and **0** duplicate keys. **5/5** correction-decision notifications were delivered. The production daily schedule was not changed. The main background worker still ran `8b843a6`; its notification/attendance/authentication source is identical to `b60f42b`. The recovery worker used the final candidate image.

The isolated failed-SMTP queue recorded **4** attempts with `ConnectionRefusedError`, while the in-app message remained. On restoring Mailpit delivery the same notification had `email_sent=True`, empty error and the same attempt history. Matching Mailpit message evidence is retained separately.

## Local TLS and security scope

**9/9** private-CA localhost TLS checks passed: verified SAN/chain, exact redirect, HSTS, TLS 1.2/1.3 acceptance, TLS 1.0/1.1 rejection, secure session cookie, and HTTPS logout. This uses an explicit test CA without disabling certificate verification. It does not validate a public certificate, domain or Internet host.

The old two-day local test certificate had expired. That failed verification was retained; the private localhost fixture was renewed, Nginx reloaded, and the nine checks repeated successfully. No operating-system trust was installed and no verification bypass was used. Temporary test sessions were revoked and private scanner authentication files removed after execution.

Three authenticated, time-bounded ZAP API scans are retained on the final candidate. Student scanning includes the API definition with auth lifecycle paths excluded; faculty/admin active scans are GET-only. Each scanner verified its actual role through an authenticated `/api/me/` response. All alerts and bounded-scan limitations remain in the assessment. No comprehensive penetration-test certification is claimed.

Local scanner startup initially timed out when three Java scanners were launched together with a 180-second allowance. The failed startup logs are retained separately; scans were rerun sequentially with a two-CPU cap and a ten-minute startup allowance, and all three completed. These are setup errors, not successful security tests. The authentication extension also corrected an initially wrong test URL before completing the 12-case run; its partial setup record is excluded from acceptance counts. During heavy local setup, Docker readiness probes briefly timed out and later recovered; the local workload is not used as the performance measurement.

## GitHub and Jira handoff

| GitHub | Jira | Technical coverage / remaining work |
| --- | --- | --- |
| [#29](https://github.com/Kundhan73/SE-MiniProject-SAMS/issues/29) | [SAM-42](https://pes1ug24am327.atlassian.net/browse/SAM-42) | Performance results above; proposed fix requires PR review/merge before it changes main. |
| [#30](https://github.com/Kundhan73/SE-MiniProject-SAMS/issues/30) | [SAM-43](https://pes1ug24am327.atlassian.net/browse/SAM-43) | Security matrix, scoped role scans and local TLS; public staging/certificate validation pending. |
| [#31](https://github.com/Kundhan73/SE-MiniProject-SAMS/issues/31) | [SAM-44](https://pes1ug24am327.atlassian.net/browse/SAM-44) | 49 browser checks and six Lighthouse snapshots; physical-device and human assistive-technology assessment pending. |
| [#37](https://github.com/Kundhan73/SE-MiniProject-SAMS/issues/37) | [SAM-48](https://pes1ug24am327.atlassian.net/browse/SAM-48) | Authentication/security retests complete within documented scope; Tarun personal review/conclusion pending. |
| [#38](https://github.com/Kundhan73/SE-MiniProject-SAMS/issues/38) | [SAM-49](https://pes1ug24am327.atlassian.net/browse/SAM-49) | Course/timetable/enrollment retests complete; Tarun personal review/conclusion pending. |
| [#39](https://github.com/Kundhan73/SE-MiniProject-SAMS/issues/39) | [SAM-50](https://pes1ug24am327.atlassian.net/browse/SAM-50) | Attendance/concurrency/audit retests complete; Tarun personal review/conclusion pending. |
| [#40](https://github.com/Kundhan73/SE-MiniProject-SAMS/issues/40) | [SAM-51](https://pes1ug24am327.atlassian.net/browse/SAM-51) | Student/correction retests complete; Tarun personal review/conclusion pending. |
| [#41](https://github.com/Kundhan73/SE-MiniProject-SAMS/issues/41) | [SAM-52](https://pes1ug24am327.atlassian.net/browse/SAM-52) | Report/filter/threshold/CSV/PDF retests complete; Tarun personal review/conclusion pending. |
| [#42](https://github.com/Kundhan73/SE-MiniProject-SAMS/issues/42) | [SAM-53](https://pes1ug24am327.atlassian.net/browse/SAM-53) | Scheduled jobs, Mailpit, failure/recovery and admin/browser checks; real external mailbox and personal review pending. |

The nine assignments remain open where human review, unavailable external resources, or review/merge of the proposed performance change is still required. Earlier implemented bugs remain closed; no new product regression was found in the final correctness suites. The owner-paused bulk Jira sync was not restarted.

## What Tarun and the team still need to supply

1. Review the case register/screenshots and personally repeat the independent checks required by the course, then post Tarun's own conclusion under DarkTJ7. The agent cannot create that personal testimony.
2. Independent teammate QA/release review of PR #54 and final integrated acceptance. No reviewer approval or faculty waiver is inferred.
3. A public staging host/domain and matching certificate for public TLS, plus an external SMTP service and controlled recipient for real external delivery. Neither resource was supplied.
4. Physical browser/device and human assistive-technology checks beyond automated emulation and accessibility snapshots, or an actual course scope decision.

## Evidence navigation

- [Live case register](Case-Register.md) and [machine-readable cases](case-register.json).
- [Final functional cases](functional-system-cases.json), [authenticated security cases](authenticated-security-cases.json), [local browser observations](local-browser-observations.json).
- `run-*/` contains original Actions artifacts, endpoint distributions, resource samples, rendered browser screenshots and coverage/JUnit reports.
- Local TLS, ZAP assessments, scheduler logs and retry/recovery proofs retain their own actual commit and environment.
- Previous 30 October evidence remains immutable in commit `ff1672622753bf4a03026a39b967be72ad7b8358`; this report does not erase its failed scale measurement.

## Full evidence archive

[Download all original reports, screenshots and artifacts](Assigned-Work-Evidence.zip). The `run-*/` folders referenced above are inside this archive.

SHA-256: `cb1628510931af6fdadbb066ca2236464a75f186539a5a1463b1efa3fce67f9a`.

[Student browser evidence](final-student-overview.png) · [Recovered Mailpit message](mailpit-recovered-email.png) · [Keyboard correction result](keyboard-correction-saved.png) · [Authentication boundaries](authentication-boundary-cases.json).
