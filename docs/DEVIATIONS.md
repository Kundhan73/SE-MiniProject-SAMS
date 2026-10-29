# Implementation addendum and deviations

Baseline: submitted SRS v1.1, SAD v1.1 and STP v1.0. Addendum date: 29 October 2026. The original PDFs are preserved.

| Baseline / mismatch | Current implementation and reason |
| --- | --- |
| Jira two-week sprints (1–14 Oct, 15–28 Oct, 29 Oct–11 Nov) | Teacher sheets take priority: 19–23 Oct, 26–30 Oct, testing 2–6 Nov. GitHub milestones reflect those windows. Original Jira sprint history is preserved and is supplementary. |
| Jira as sole backlog | Teacher explicitly requires a linked GitHub Project. GitHub issues, estimates and milestones are created. Project creation needs the owner's missing `project` OAuth scope. |
| Django apps contain module-specific views | Domain models/services retain separate apps. A shared `core/api.py` composes endpoint adapters and standard input/error handling to keep the small team's API consistent. |
| HTMX and Bootstrap | Django templates and a small JavaScript client provide the role interfaces without a frontend build or external JavaScript dependencies. Responsive CSS is custom. |
| bcrypt | Django's salted PBKDF2 password hashing in production, an equivalent adaptive hash allowed by the SRS. Fast MD5 hashing is used only in automated test settings. |
| SimpleJWT refresh blacklist | Each issued JWT family has a database LoginSession. Access and refresh both check active status and inactivity; API and web logout revoke the associated family. This provides immediate access revocation as well as refresh revocation. |
| Stateless JWT alongside idle timeout | A server-side session record is deliberate: enforcing real inactivity and immediate logout requires server state. Browser UI uses HttpOnly, CSRF-protected Django sessions. |
| WeasyPrint | ReportLab creates actual PDF reports without native rendering dependencies. CSV exports neutralize spreadsheet formulas. |
| Selenium | Playwright/Chromium executes the browser regression workflows. The scenarios and purpose remain the same. |
| Jenkins as only pipeline | GitHub Actions is the hosted pipeline required by Part 2. Jenkinsfile and SonarQube configuration are retained; their execution needs an external server. |
| Automatic deployment | Tested images are automatically published to GHCR after green main CI. Remote deployment needs a selected host/domain; no provisioned server is assumed. |
| PostgreSQL everywhere | SQLite is available for quick local demos/unit tests. CI also tests PostgreSQL. Docker uses PostgreSQL. SQLite is not the concurrency/load-test deployment target. |
| Old README lists Anish as PES1UG24AM343 | Original SRS/SAD/STP consistently list PES1UG24AM348. README now follows the submitted documents; team confirmation remains advisable. |

No historical PR, review, sprint completion, teacher approval or uptime evidence has been manufactured. Any recordings created now are retrospective demonstrations of the current working build, not evidence recorded during the original sprint window.
