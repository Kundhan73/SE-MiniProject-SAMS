# SAM-44 / GitHub #31 accessibility follow-up

Execution: 3–4 November 2026 (Asia/Kolkata). The local isolated SAMS stack used a synthetic database and the current implementation branch. Browser interactions were **Codex-assisted on Tarun's laptop**; this report does not claim Tarun's personal tester sign-off. Screenshots labelled `iab` come from the Codex in-app browser. A narrow browser viewport is **not** a physical Android or iOS browser.

## Commits and environment

- Baseline tested: `4e3eddb726441d7b091e00dabc606e4b6411c7b8` (`main` when the follow-up began).
- Roster accessibility fix tested: `f7bf7471b961aa9346c492f02cccf3d1706f3b1d` (authored and committed by `TARUN.J <187250293+DarkTJ7@users.noreply.github.com>`). The deployed `/app/staticfiles/app.js` SHA-256 matched the committed file: `a1ee87b7f2b814aba2f10a85efa03ec6720b5810717032a2f6b40ba642326162`.
- App: isolated Docker Compose, `http://localhost:8003`, demo student `STU001`, faculty `FAC001`, administrator `ADM001`. A single fresh 3 November synthetic CS341/F session was added to exercise the 100-student roster; no production data was used.
- Pre-existing automated evidence on the earlier branch remains in `docs/testing/tarun-2026-11-02`: 49 browser/axe checks and six Lighthouse accessibility scores of 100. Those runs are **not** represented as newly executed on `f7bf747`.

## Interactive case register

| ID | Expected | Actual observation | Result | Commit tested | Evidence |
|---|---|---|---|---|---|
| UX-01 | Student login works with keyboard; Tab moves from Institute ID to Password. | Tab focused the Password field; Enter signed in as STU001. | Pass | `4e3eddb` | [Student overview](student-overview-iab.png) |
| UX-02 | Student overview and navigation remain usable at a narrow width without document-wide horizontal scroll. | At 416 CSS px, the page width was 401 px; Overview, Corrections and Notifications were exposed as named controls. | Pass at 416 px; exact 360 px covered only by earlier automation | `4e3eddb` | [Student overview](student-overview-iab.png) |
| UX-03 | Student correction controls have names and tab order; existing records display as text. | Class record, Correct status, Reason and Send to faculty were labelled; Tab moved from Corrections to Notifications. Synthetic markup in earlier correction reasons appeared as plain text. | Pass for observed scope | `4e3eddb` | [Corrections](student-corrections-iab.png) |
| UX-04 | Student notifications are readable; logout returns to sign-in. | Notification text and Mark read buttons were exposed; Sign out returned to the login page. | Pass | `4e3eddb` | [Notifications](student-notifications-iab.png) |
| UX-05 | Every faculty attendance status control identifies the associated student. | **Before fix:** all 100 controls were announced only as “Status.” **After fix:** 100 controls were announced as “Attendance status for Student NNN (STUNNN)”; Tab from Student 001 moved to Student 002. The visible label remains “Status.” | Fail on baseline; pass on fix | `4e3eddb` → `f7bf747` | [Roster screenshot](faculty-roster-fixed-iab.png), [accessibility tree](faculty-roster-accessibility.txt) |
| UX-06 | Faculty report filters and exports have named controls; wide table can be keyboard-scrolled. | Course, Institute ID, date and report controls had names; CSV/PDF export links were named; the report table had `role=region` and `tabindex=0`. | Pass for observed controls | `f7bf747` | [Faculty reports](faculty-reports-iab.png) |
| UX-07 | Admin overview and reports fit a narrow viewport with an independently scrollable table. | At 416 CSS px, the document width was 401 px. The report region was 337 px wide with 498 px scroll width, `aria-label="Student table"`, and `tabindex=0`. | Pass at 416 px; exact 360 px covered only by earlier automation | `f7bf747` | [Admin overview](admin-overview-narrow-iab.png), [admin reports](admin-reports-narrow-iab.png) |
| UX-08 | Admin account form fields have names and keyboard order. | Institute ID, Name, Email, Initial password and Role were labelled; Tab from Institute ID focused Name. No account was created. | Pass for observed form | `f7bf747` | [People](admin-people-iab.png) |
| UX-09 | Actual Android Chrome: login, four core screens where role permits, keyboard/touch, no horizontal page overflow at 360 px. | Samsung A56 detected by Windows as MTP, but ADB still lists no device; no phone-browser observation recorded yet. Private Wi-Fi route is being prepared. | Pending | — | — |
| UX-10 | Actual iOS Safari: login and responsive observations. | No iPhone or existing real-device service available in this test environment. WebKit emulation is recorded in earlier automated evidence, not represented as actual iOS Safari. | Pending | — | — |

## Change and acceptance status

`static/app.js` gives each roster select a unique accessible name including the student name and institute ID. `templates/dashboard.html` requests a versioned JavaScript URL so an existing browser loads the corrected script after deployment. `node --check static/app.js` and `git diff --check` passed. The browser retest and the deployed-vs-commit SHA check passed.

GitHub #31 / Jira SAM-44 remains **open** while the actual device observations are outstanding. Tarun should review the evidence personally and post his own tester conclusion; this report is an assisted execution record, not that conclusion.
