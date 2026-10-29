# Demo and recording guide

Use only synthetic demo data. Password for ADM001, FAC001 and STU001 is `DemoPass@1234`. Start the local or Docker app as described in README. Today's faculty sessions depend on the actual date; the seed creates slots for the date it is run.

## One-minute Sprint 1 scope

- 0–15 s: Show sign-in, then Admin overview and role-restricted navigation.
- 15–35 s: Academic setup: existing courses, faculty/section links, timetable and CSV enrollment form.
- 35–50 s: People: user roles and account access. Sign out and demonstrate a student dashboard.
- 50–60 s: Show GitHub Actions checks for the actual PR/commit.

## Two-minute Sprint 2 scope

- 0–35 s: FAC001 → Take attendance. Show the 60-student roll, change an exception to Absent/On Duty, submit and reopen the saved session.
- 35–65 s: STU001 → course percentages and Corrections; request a correction with a reason on own attendance.
- 65–90 s: FAC001 → Corrections; approve the request. Open Reports and download CSV/PDF or show the defaulter list.
- 90–110 s: ADM001 → Audit trail; show editor, previous/new status, timestamp and reason.
- 110–120 s: Show actual passing CI and generated report files.

Record the working application with the normal macOS screen recorder. New recordings made on/after 29 October must be labelled retrospective, especially the first sprint whose original window has ended. Do not describe current recordings as historical sprint evidence. Suggested paths: `docs/demos/sprint-1-retrospective.webm` and `docs/demos/sprint-2-demo.webm` (or `.mp4`).

Use a separate browser profile or separate sessions to keep roles clear. Never record a real password, SMTP secret, personal student data or an authentication token. The synthetic demo password is intentionally public.

## Explain the pipeline

A PR triggers checks. Tests exercise SQLite and PostgreSQL, security audit checks dependencies, browser tests exercise the product, and the container job proves the image starts. Failed required checks block review/merge when main protection is configured. After a reviewed merge to main, green CI triggers image delivery to GHCR. Deployment needs a configured server; publishing an image alone does not mean a website is already hosted.
