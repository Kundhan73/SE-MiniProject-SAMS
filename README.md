# SAMS · Student Attendance Management System

UE24CS341A Software Engineering · PES University · AIML Section F

[![CI](https://github.com/Kundhan73/SE-MiniProject-SAMS/actions/workflows/ci.yml/badge.svg)](https://github.com/Kundhan73/SE-MiniProject-SAMS/actions/workflows/ci.yml)

SAMS records attendance against scheduled classes, gives students a private attendance view, and routes corrections to the responsible faculty member. Faculty and administrators can export reports; every attendance change has an append-only audit entry.

## Run the local demo

Requires Python 3.12 or later. The quick demo uses SQLite; Docker uses PostgreSQL.

```bash
git clone https://github.com/Kundhan73/SE-MiniProject-SAMS.git
cd SE-MiniProject-SAMS
git switch implementation/sams-ci-delivery
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements-dev.txt
python manage.py migrate
python manage.py seed_demo
python manage.py runserver
```

Open http://127.0.0.1:8000. Synthetic demo accounts share password `DemoPass@1234`:

| Role | Institute ID | What to demonstrate |
| --- | --- | --- |
| Admin | ADM001 | Courses, sections, timetable, CSV enrollment, users, threshold, audit |
| Faculty | FAC001 | Today's sessions, P/A/OD attendance, audited edits, correction decisions, reports |
| Student | STU001 | Own course percentages, records, correction requests, notifications |

The seed creates 60 students, 2 faculty, 3 courses, six weeks of synthetic attendance and today's unsubmitted sessions. It refuses to overwrite an existing database. For a fresh database with 2,000 students and 100 faculty, use `python manage.py seed_demo --full`. Demo accounts and example secrets are only for an isolated demo.

Local email appears in the terminal. The Docker stack captures email at http://localhost:8025. Forgot-password links expire in 30 minutes and work once.

## Docker

Install Docker Desktop with Compose v2.24.4 or later, then:

```bash
cp .env.example .env
docker compose up --build -d
docker compose exec web python manage.py seed_demo
```

Open http://localhost:8000. PostgreSQL, Redis, Celery worker/beat, Mailpit, Gunicorn and Nginx run together. Persistent PostgreSQL storage survives container restarts. See [deployment instructions](docs/DEPLOYMENT.md) for TLS, backups and production settings.

## Verify

```bash
ruff check .
ruff format --check .
python manage.py check
python manage.py makemigrations --check --dry-run
pytest --cov --cov-report=xml:docs/reports/coverage.xml --junitxml=docs/reports/junit.xml
python scripts/test_reports.py
pip-audit
```

With the local demo server running, `python scripts/browser_smoke.py` exercises all three roles in Chromium. Install the browser once with `playwright install chromium`. Use an isolated demo database: this test submits attendance and approves a correction.

## CI and delivery

Every PR runs linting, migration validation, SQLite and PostgreSQL tests, coverage gates, a dependency audit, real browser workflows, and a Docker build/health test. Reports are downloadable from the Actions run. `Required checks` summarizes the gate.

After a reviewed PR merges to `main` and main-branch CI succeeds, Delivery publishes `ghcr.io/kundhan73/se-miniproject-sams:sha-<commit>` and `:latest`. This is continuous delivery of a tested image. Deployment to a college VM needs a provisioned host/domain and remains an operator step. Jenkins and SonarQube configuration are also included for the submitted architecture; Jenkins requires an external server and SonarQube credentials.

## Team and roles

| Member | SRN | GitHub | Project role | Responsibility |
| --- | --- | --- | --- | --- |
| Kundhan Vudutha | PES1UG24AM327 | Kundhan73 | Developer | All application modules, bug fixes, migrations, CI/CD and deployment configuration |
| Tarun J | PES1UG24AM304 | DarkTJ7 | Tester | Test design/execution, defect reports and retesting, browser/security/performance checks |
| Anish | PES1UG24AM348 | planetai05 | QA | Requirements and coverage review, traceability, evidence review, PR quality and release readiness |

Implementation stories are assigned to the Developer. Separate testing tasks belong to the Tester; QA and release-review tasks belong to QA. These project responsibilities are separate from the application's Student/Faculty/Admin access roles. GitHub is the current assignment system; Jira is retained as a reference backlog.

## Assignment and tracking

The teacher's required windows are Sprint 1: **19–23 October**, Sprint 2: **26–30 October**, and testing/optional Sprint 3: **2–6 November 2026**. The older Jira board used different two-week windows. [GitHub issues](https://github.com/Kundhan73/SE-MiniProject-SAMS/issues) and [milestones](https://github.com/Kundhan73/SE-MiniProject-SAMS/milestones) hold the recovery backlog, points and verified assignees. Tracking created on 29 October does not represent historical work during the earlier sprint.

The [linked GitHub Project](https://github.com/users/Kundhan73/projects/1) contains the backlog, story points, assignees, project roles and teacher-aligned sprint fields. Use `python scripts/sync_github_backlog.py --project` to synchronize it from `docs/backlog.json`. See [team responsibilities](docs/TEAM_ROLES.md) for testing and QA handoffs.


## Documents

- Project specifications: [SRS](docs/SAMS_SRS.pdf), [architecture and design](docs/SAMS_SAD.pdf), [test plan](docs/SAMS_Test_Plan.pdf)
- Current implementation: [API](docs/API.md), [design deviations](docs/DEVIATIONS.md), [test-plan addendum](docs/TEST_PLAN_ADDENDUM.md), [traceability matrix](docs/TRACEABILITY.md)
- Submission status: [delivery checklist](docs/SUBMISSION_CHECKLIST.md), [demo guide](docs/DEMO_GUIDE.md)
- Actual execution evidence: [reports](docs/reports), [Actions](https://github.com/Kundhan73/SE-MiniProject-SAMS/actions)

The current PDFs include the revised three-member team allocation. Technical requirements remain the baseline; addenda describe implementation and remaining validation. Review and UAT signatures are pending actual approval.
