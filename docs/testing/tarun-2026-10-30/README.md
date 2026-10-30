# SAMS remaining validation — 30 October 2026

[Download the complete evidence archive](SAMS-Final-Validation-2026-10-30.zip) · [Case register](Validation-Cases.csv) · [Unsigned human review checklist](Human-Review-Checklist.md)

**Conclusion: HOLD overall acceptance.** The normal-load target, targeted local security checks and expanded automated accessibility checks passed for the commits and environments below. The 300-client scale run missed the latency target. Public TLS, real external mailbox delivery, physical-device/assistive-technology review and Tarun's independent personal sign-off are not established.

This is **Codex-assisted execution from DarkTJ7's account**. It does not state that Tarun personally operated every test or approved a release. GitHub's existing planetai05 approval of PR #1 at `05ce028` remains a separate record; the additional PR #50 fixes need their own review/integration.

| Work item | Observed result | Status |
|---|---|---|
| #29, normal performance | 100 distinct faculty accounts, 100 concurrent clients for 600.03 seconds after full spawn; 34,320 requests, zero failures; aggregate p95 150 ms; 40 complete attendance submissions | PASS for recorded normal-load profile |
| #29, scale performance | 300 concurrent clients for 120.06 seconds after full spawn; 35,701 requests, zero failures; p95 3,100 ms | Latency target missed; bottleneck recorded |
| #30, authenticated checks | 33 live HTTP cases passed, covering every schema-described student-forbidden administrator/faculty operation, cross-user/faculty references, injection inputs, malformed JSON, credential-field exposure and logout-token revocation | Targeted cases PASS |
| #30, authenticated ZAP | Student identity verified before a bounded active OpenAPI API scan; 20 scoped paths, 51 imported URLs, 130 total URLs; 118 PASS groups, three WARN groups, zero FAIL-rule hits | Completed for stated scope; warnings triaged |
| #30, local live TLS | Nine checks passed: certificate verification with an explicit private CA, TLS 1.2/1.3, rejection of 1.0/1.1, exact HTTP redirect, HSTS, secure session cookie and HTTPS logout | Local transport PASS; public TLS blocked |
| #31, browsers/accessibility | 48 screen/width/browser combinations plus interactive API documentation = 49 passed; six Lighthouse snapshots scored 100; zero tested axe A/AA violations and zero page-level horizontal overflow | Automated scope PASS; actual-device/human AT coverage remains |
| Notifications | Earlier recorded accelerated scheduling, 2,000 notification/email deliveries to Mailpit, four-attempt SMTP exhaustion, retained in-app notification and recovery delivery remain linked below | Local evidence retained; real mailbox and full-day observation remain pending |
| Automated regression | 140 local pytest tests passed; XML coverage/JUnit and four reports regenerated; statement coverage 99.87%, branch coverage 97.06%; all seven standard CI jobs passed | PASS on final candidate |

## Commits and reproducible evidence

- Integrated implementation tested for sustained performance, HTTP security and local TLS: `05ce0282959ab2084b553bcd1e43aa312961d21c` on `implementation/sams-ci-delivery`.
- Final PR #50 candidate for fixes, 140-test local regression, expanded browser acceptance and restored laptop app: `db0c84c17f1dcc2d6b008dd93321b8aeb77f8af0`.
- Performance harness revision: `e5a4f7233c60120944a340713ebf78027ea66798`; application checkout was pinned to the integrated implementation above.
- [Full sustained-load CI run](https://github.com/Kundhan73/SE-MiniProject-SAMS/actions/runs/40936392200). Its overall failure deliberately preserves the 300-client latency miss; the 100-client acceptance step passed.
- [Final browser/accessibility run](https://github.com/Kundhan73/SE-MiniProject-SAMS/actions/runs/41068862247), 49/49 passed on the exact candidate head.
- [Final standard CI run](https://github.com/Kundhan73/SE-MiniProject-SAMS/actions/runs/41068868532), seven successful jobs, including SQLite/PostgreSQL tests, browser workflows, dependency audit, Docker smoke, short load check and required-check gate.

`Validation-Cases.csv` and `Validation-Cases.json` contain test IDs, expected/actual results, pass/fail or blocked state, tested commit and evidence paths. JUnit contains the individual automated cases. Screenshots, axe reports, accessible-name/role snapshots, keyboard traces, Lighthouse HTML/JSON, Locust CSV/HTML, duration records and CI job metadata are included.

## Performance environment and limits

The isolated Ubuntu/Linux Docker application, PostgreSQL, Nginx and Redis shared CPU set `0,1`; the load client used separate CPU set `2,3`. App/database/proxy/Redis container memory caps sum to 3.25 GiB. Background worker/beat were not started during load validation. This tests the stated two-core/below-four-GiB service budget, not a public college network or a provisioned staging server.

The fresh synthetic fixture contained 2,000 students, 100 faculty, 20 sections and 12,000 historical attendance records. Forty current-day sessions were marked during the normal profile. The 0.5-client/s ramp respects the unchanged production anonymous-login throttle; all ramp/login traffic remains included in statistics and production password hashing was retained. The scale profile reused the 100 faculty identities across 300 clients and followed the normal profile, so its sessions were already submitted and it performed no additional marking. Faculty without a section have empty scoped results; these profiles do not establish every possible all-active-teacher workload.

Normal-profile endpoint p95s: roster 150 ms, summary 150 ms, attendance submission 190 ms, faculty login 340 ms. At 300 clients, roster/summary/login p95s reached about 3.1 seconds. The deployed source uses two synchronous Gunicorn workers; application log processing times were substantially below end-to-end scale latency. Queueing at constrained service capacity is a plausible bottleneck, not a CPU-profiling conclusion. The resource stream returned unavailable values (`--`), so no measured CPU-saturation claim is made. Before accepting 300-client capacity, profile worker/SQL queueing, evaluate a deployment change and repeat the scale profile. The test plan permits a documented scale bottleneck; that does not turn a missed three-second target into a pass.

The earlier failed/incomplete laptop load attempts remain in the prior report. The successful hosted profile does not erase them. See `performance-provenance-note.md` for a descriptive origin-label error in the unmodified original fixture metadata; CI logs establish fresh seeding, while the private snapshot was used only for localhost security/TLS.

## Security interpretation

Role replay covered all administrator/faculty operations described as restricted in the generated schema. Separate live requests checked foreign student correction records, another faculty's submission/edit/decision, literal SQL/XSS inputs, malformed JSON, user response fields and rejection of access/refresh tokens after logout. In the actual Chromium UI, a stored `<img ...>`/`<script>` reason appeared as text, with zero image/script elements created in the content region.

The active ZAP scan used a verified student bearer token scoped to loopback. Authentication lifecycle endpoints were excluded so the scanner could not invalidate its own identity; explicit cases covered logout/revocation separately. The six-minute active-scan cap is recorded. This is bounded authenticated evidence, not exhaustive administrator/faculty-authorized penetration testing. Its three warnings were low severity: known version disclosure and missing resource policy at integrated `05ce028` (tracked/fixed in PR #50), and HTML 404 responses to generated nonexistent paths. Full alert details and triage are retained. A rule-level PASS is not evidence that public HTTPS was exercised by this HTTP API scan.

Local TLS used source Nginx TLS settings with a localhost port override and production Django security flags. The test client explicitly trusted the generated local CA and kept certificate verification enabled. No CA was installed into Windows, no browser security warning was bypassed and no private key or token is included. A private localhost certificate is not a publicly trusted staging certificate.

## Accessibility fixes and retests

New defect [#51](https://github.com/Kundhan73/SE-MiniProject-SAMS/issues/51): overflowing tables were not keyboard focusable. The fix adds a named region and tab stop; arrow-key scrolling passed across all four engines. A separate laptop retest reached the region by six Tab presses and moved its scroll position from 0 to 34 pixels with Right.

New regression [#52](https://github.com/Kundhan73/SE-MiniProject-SAMS/issues/52): strict CSP prevented Swagger initialization/CDN loading. The fix uses a pinned same-origin sidecar, external initializer and external stylesheet. The laptop and CI rendered 32 operations with no inline scripts/styles or console warnings/errors. The application retains its strict same-origin script policy. Existing #47 labels and #49 headers remain part of PR #50.

Final browser versions: Google Chrome 156.0.8078.79, Microsoft Edge 156.0.4314.56, Firefox 157.0 and WebKit 27.2. Chrome/Edge are actual vendor channels; Firefox/WebKit are Playwright test builds. Screens covered login, student attendance, faculty roster, administrator reports, academic setup and people at widths 1280 and 360. WebKit/360 is not a claim of testing Safari on a real iPhone. Accessible-name/role snapshots and keyboard tests support semantic checks; they are not a human screen-reader usability sign-off.

The first audit attempt failed because its instrumentation violated CSP. A corrected attempt found unfocusable scroll regions and captured transient contrast warnings during the entrance fade. The final run waits for animations/fonts/network to settle. Its 48 axe checks found no tested violations and all six Lighthouse snapshots scored 100. Earlier observations remain available and are not silently overwritten.

## Notifications and remaining acceptance

[Previous detailed notification and manual evidence](https://github.com/Kundhan73/SE-MiniProject-SAMS/blob/e73a43cca95caf196c1c0a0244d7c81b7cf4bd16/docs/testing/tarun-2026-10-29/README.md) records the accelerated Celery schedule, Mailpit recipients/body, retry exhaustion, administrator-only failure listing, preserved in-app message and successful recovery. The ten-second test schedule is distinct from the normal 86,400-second schedule; a full-day production timing observation has not been established.

Tarun confirmed on 30 October that no staging domain, external SMTP service or real test recipient is available. Public certificate/TLS and real external mailbox delivery therefore remain **BLOCKED**, unless those resources are supplied or faculty explicitly accepts a waiver. Real iOS/Android and human assistive-technology checks remain unexecuted. No waiver or approval is implied.

The laptop app has been restored at http://localhost:8000 and Mailpit at http://localhost:8025 with the preserved synthetic database. `Human-Review-Checklist.md` is intentionally unsigned. Tarun must add his own observations and conclusion; this report publishes an assisted technical conclusion only. New fixes are reviewable in [PR #50](https://github.com/Kundhan73/SE-MiniProject-SAMS/pull/50). No open issue is closed merely because a scoped test passed.
