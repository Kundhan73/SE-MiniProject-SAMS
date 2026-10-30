# SAMS 15-Minute Final Demo Presentation Deck & Delivery Guide

**Course:** UE24CS341A — Software Engineering Mini-Project  
**Institution:** PES University, Bengaluru  
**Project:** Student Attendance Management System (SAMS)  
**Document Version:** 1.0  
**Effective Date:** 30 October 2026  
**Accountable QA Owner:** Anish (`planetai05`), QA Engineer  
**Related Issue:** [#33](https://github.com/Kundhan73/SE-MiniProject-SAMS/issues/33) (SAM-46)  

---

## 1. Presentation Structure and Timing Budget

| Segment | Duration | Presenter | Topics Covered |
| :--- | :--- | :--- | :--- |
| **Part 1: Context & Architecture** | 0:00 – 3:00 | **Anish (QA)** | Problem statement, objectives, team roles, architecture, and backlog governance. |
| **Part 2: Live Application Demo** | 3:00 – 8:30 | **Kundhan (Dev)** | Faculty marking, student view, correction dispute workflow, reports, CSV/PDF, admin audit trail. |
| **Part 3: QA, Testing & Performance** | 8:30 – 12:00 | **Tarun (Tester)** | Automated test execution, 100% statement coverage, Locust target-scale load test, security & bug fixes. |
| **Part 4: Operations & Maintenance** | 12:00 – 13:30 | **Anish (QA)** | Backup runbooks, disaster recovery (RTO/RPO), container rollback, and working-hours uptime monitoring. |
| **Part 5: Wrap-Up & Evaluator Q&A** | 13:30 – 15:00+ | **All Team Members** | Retrospective summary, SDLC artifacts checklist, and technical defense. |

---

## 2. Slide Deck Outline (15 Slides)

### Slide 1: Title & Team Introduction
- **Header:** Student Attendance Management System (SAMS) — UE24CS341A Final Defense
- **Content:**
  - Kundhan Vudutha (`PES1UG24AM327`) — Developer
  - Tarun J (`PES1UG24AM304`) — Tester
  - Anish (`PES1UG24AM348`) — QA Engineer
  - GitHub: `Kundhan73/SE-MiniProject-SAMS` | Linked Project: `projects/1`

### Slide 2: The Academic Problem & Core Mission
- **The Challenge:** Manual roll-calls consume 10% of lecture time; paper records invite proxy attendance; delayed student deficit warnings; vulnerable audit trails.
- **The Solution (SAMS):**
  - Single-screen batch marking (< 60s for 60 students).
  - Automated Celery alerts when attendance falls below 75%.
  - Transparent 7-day correction dispute workflow.
  - Append-only database triggers preventing audit tampering.

### Slide 3: Agile Process & GitHub Backlog Governance
- **Sprint Schedule:**
  - Sprint 1 (19–23 Oct): Auth, Scaffolding, Models, CSV Enrollment.
  - Sprint 2 (26–30 Oct): Roll Marking, Student View, Corrections, Reports, Audit.
  - Testing & Hardening (2–6 Nov): QA Review, Load Tests, Bug Fixes, Maintenance Plan.
- **Board Metrics:** 43 issues, 112 story points, 0 backlog mismatches.

### Slide 4: System Architecture & Technology Stack
- **Architecture Diagram:** Layered MVC + Service-Layer design.
- **Components:**
  - Presentation: Server-rendered Django templates + Vanilla JS (no heavy build step).
  - API: Django REST Framework with OpenAPI 3.0 schema.
  - Processing: Celery + Redis for asynchronous notification queues.
  - Database: PostgreSQL 16 with native triggers.
  - Gateway: Nginx reverse proxy with TLS and security headers.

### Slide 5: Database Schema & Immutability Architecture
- **Normalized Data Model:** Users, Courses, Sections, TimetableSlots, ClassSessions, AttendanceRecords, AuditLogs.
- **Forensic Security:** PostgreSQL trigger `audit_auditlog_prevent_mutation` aborts any SQL `UPDATE` or `DELETE` on the audit log.

### Slide 6: Live Demo Walkthrough — Faculty Roll Marking (3:00 - 5:00)
- **Demo Steps:**
  1. Sign in as `FAC001` (`DemoPass@1234`).
  2. Open today's class session from the daily timetable.
  3. Rapidly mark a 60-student class; toggle exceptions (Absent, On Duty).
  4. Submit session in under 60 seconds.
  5. Demonstrate duplicate marking prevention: double-submission is blocked with HTTP 409 Conflict.

### Slide 7: Live Demo Walkthrough — Student Portal & Correction Disputes (5:00 - 6:30)
- **Demo Steps:**
  1. Sign in as `STU001` (`DemoPass@1234`).
  2. View course-wise attendance percentage and warning indicators (< 75%).
  3. Select an incorrectly marked lecture and submit a formal Correction Request with justification.

### Slide 8: Live Demo Walkthrough — Faculty Decision & Report Generation (6:30 - 7:30)
- **Demo Steps:**
  1. Return to `FAC001` -> Pending Corrections.
  2. Approve the correction request with an audit note.
  3. Open Reports; filter by Course and Date Range.
  4. Export CSV (formula injection protection verified).
  5. Export ReportLab PDF (paginated, formatted, handling 0-class students cleanly).

### Slide 9: Live Demo Walkthrough — Administrator Governance & Audit Trail (7:30 - 8:30)
- **Demo Steps:**
  1. Sign in as `ADM001` (`DemoPass@1234`).
  2. Show bulk student enrollment via CSV with atomic parsing.
  3. Open the immutable Audit Trail: observe the automated record of the faculty's correction decision with previous status, new status, timestamp, and user ID.

### Slide 10: Automated Testing & 100% Statement Coverage (8:30 - 10:00)
- **Suite Metrics:** 142 automated tests executed in 3.15s (0 failures).
- **Quality Gates:**
  - Statement Coverage: **100.00%** (761/761 statements, gate >= 80%).
  - Branch Coverage: **98.24%** (167/170 branches, gate >= 70%).
- **Provenance Separation:** Reports distinctly label local unit results from separate browser/performance artifacts.

### Slide 11: Target-Scale Load Testing & Security Validation (10:00 - 11:00)
- **Locust Load Test (SAMS-NF-001):**
  - Database scale: 2,000 students, 100 faculty, 30 sections.
  - 20 concurrent users executing marking and reporting workflows.
  - 393 requests with 0% failures.
  - **95th Percentile Response Time:** 1.40s (Target: < 3.00s).
- **Security Audit:** `pip-audit` confirms 0 known vulnerabilities. PBKDF2 hashing & 15-minute brute-force lockout verified.

### Slide 12: Discovered Bugs & Triage Case Studies (11:00 - 12:00)
- **Case 1 (Bug #45):** PDF export appended `%` to `No classes`. Fixed in `reports/services.py` with regression test.
- **Case 2 (Bug #46):** Test report provenance confusion. Fixed in `scripts/test_reports.py` with regression test.
- **Case 3 (Health Check Defect):** Database connection errors threw unhandled 500s. Fixed in `core/api.py` to return HTTP 503 `{"status": "unavailable"}` with `test_health_db_outage`.
- **Case 4 (Bugs #47, #49, #51, #52):** Admin label deduplication, proxy headers, mobile keyboard table scrolling, and strict CSP documentation addressed in PR #50.

### Slide 13: CI/CD Pipeline & Delivery Automation (12:00 - 12:45)
- **GitHub Actions Pipeline:** 7 parallel and sequenced jobs (lint, migration check, SQLite/PostgreSQL matrix, coverage gates, browser smoke, container build, load gate).
- **Container Registry:** Automatic publishing of immutable commit-SHA tagged images to GHCR upon main merge.

### Slide 14: Product Maintenance Plan & Uptime SLA (12:45 - 13:30)
- **Backup & Recovery:** Daily `pg_dump -Fc` with SHA-256 checksums; RTO <= 2h, RPO <= 24h.
- **Container Rollback:** Documented SHA-image override runbook for zero-downtime recovery.
- **Working-Hours Uptime Monitoring:** `scripts/monitor_uptime.py` tracking 99.0% availability during 8am–6pm Mon–Sat, excluding Sunday maintenance windows (00:00–06:00 IST).

### Slide 15: Conclusion & Q&A Defense (13:30 - 15:00)
- **Summary:** Complete, functional, secure, and rigorously tested academic attendance system.
- **Artifacts Handed Over:** SRS v1.2, SAD v1.2, STP v1.2, Maintenance Plan, Traceability Matrix, Final Jackfruit Academic Report, and working Chromium recordings (`docs/demos/`).
- **Open Floor for Evaluator Questions.**

---

## 3. Evaluator Q&A Preparation: Anticipated Questions & Defenses

1. **Q: Why didn't you use pure stateless JWT authentication if it is an API?**  
   *A:* Pure stateless JWT tokens cannot be revoked immediately upon user signout or administrator suspension without maintaining server-side state. SAMS couples SimpleJWT token families with a database `LoginSession` record, providing immediate session revocation upon logout and enforcing strict 30-minute inactivity timeouts while maintaining REST stateless advantages for short-lived access tokens.

2. **Q: How do you guarantee the audit log cannot be tampered with by a rogue administrator?**  
   *A:* Application code and Django ORM permissions enforce read-only access to audit logs. Additionally, at the database level, PostgreSQL triggers (`audit_auditlog_prevent_mutation`) explicitly intercept any SQL `UPDATE` or `DELETE` statement on `audit_auditlog` and raise an exception, preventing direct database modifications.

3. **Q: How does the system handle high concurrency when multiple faculty submit attendance simultaneously?**  
   *A:* Attendance submission uses atomic database transactions with database-level unique constraints on `(session_id, student_id)`. Bounded query budgets (enforced in `test_roster_query_count_does_not_grow_per_student`) ensure constant query counts regardless of class size. Our Locust load test proved sustained execution across 20 concurrent faculty users at p95 latency of 1.40s.

4. **Q: What happens if an email notification fails to send?**  
   *A:* Emails are dispatched asynchronously through Celery workers. If the SMTP gateway fails, exceptions are logged in the `Notification` table with attempt counts, timestamps, and error messages (`email_attempts` and `email_error`), visible in the administrator email failure dashboard (`/api/admin/email-failures/`).

5. **Q: Why use ReportLab instead of WeasyPrint as originally proposed?**  
   *A:* WeasyPrint requires complex native OS dependencies (Pango, Cairo, GDK-PixBuf) which introduce container bloat and cross-platform installation fragility. ReportLab is pure Python, produces deterministic, lightweight, paginated PDFs, and integrates seamlessly across Windows development, Linux CI runners, and production Docker containers.

---

## 4. Supporting Demo Media
For evaluation review, real silent Chromium recordings captured against synthetic data are archived in the repository:
- `docs/demos/sprint-1-retrospective.webm` (60 seconds): Authentication, role dashboards, and course setup.
- `docs/demos/sprint-2-demo.webm` (120 seconds): Live roll marking, student view, correction dispute flow, reports, and audit history.
