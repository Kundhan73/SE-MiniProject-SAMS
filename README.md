# SAMS: Student Attendance Management System

UE24CS341A Software Engineering, Jackfruit Mini-Project
PES University, Bengaluru | B.Tech CSE (AIML) 2024 batch, Section F

## Team

| Name | SRN | Ownership |
| --- | --- | --- |
| Kundhan Vudutha | PES1UG24AM327 | Authentication and RBAC, Administration and Audit log, CI/CD, security validation |
| Tarun J | | Course, section and timetable management, Notifications |
| Tejaswini S | PES1UG25AM815 | Attendance marking, Correction request workflow |
| Anish | | Student attendance view, Reports and Defaulter list, CSV/PDF export |

## About

SAMS is a web application for recording student attendance per class session and generating attendance reports without manual compilation.

- Faculty mark Present / Absent / On Duty for each timetabled session from one screen
- Students see their attendance percentage per course and can raise correction requests
- Reports per student, per course and per date range, plus a defaulter list below a configurable threshold (CSV / PDF export)
- Email and in-app notifications for low attendance and pending corrections
- Admin manages users, roles, courses, timetables and the threshold, with an append-only audit log of every attendance edit

**Stack:** Python, Django, Django REST Framework, PostgreSQL, Celery + Redis, Docker, Jenkins, SonarQube, pytest

## Submissions

| Deliverable | Due | File |
| --- | --- | --- |
| Software Requirements Specification | 06-09-2026 | `docs/SAMS_SRS.docx` |
| Software Architecture and Design (component design) | 30-09-2026 | [`docs/SAMS_SAD.pdf`](docs/SAMS_SAD.pdf) ([docx](docs/SAMS_SAD.docx)) |
| Test Plan | 02-10-2026 | [`docs/SAMS_Test_Plan.pdf`](docs/SAMS_Test_Plan.pdf) ([docx](docs/SAMS_Test_Plan.docx)) |

UML sources (Mermaid) and rendered diagrams are in [`docs/diagrams`](docs/diagrams).

## Agile tracking

Jira Scrum project **SAM** (board: SAM board) holds the product backlog: 9 epics, user stories with acceptance criteria and story points, and three two-week sprints.

| Sprint | Dates | Goal |
| --- | --- | --- |
| Sprint 1 | 01-10 to 14-10 | Project scaffold, CI/CD, authentication, course and timetable setup |
| Sprint 2 | 15-10 to 28-10 | Attendance marking, student view, correction workflow |
| Sprint 3 | 29-10 to 11-11 | Reports, notifications, admin and audit, performance and security validation |

## Planned repository layout

```
docs/                 SRS, SAD, Test Plan, diagrams
sams/                 Django project (core, accounts, courses, attendance, reports, notifications, audit)
docker/               Dockerfiles, nginx config
Jenkinsfile           CI/CD pipeline
docker-compose.yml
```
