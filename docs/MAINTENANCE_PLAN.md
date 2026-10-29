# SAMS Product Maintenance Plan

**Document Version:** 1.0  
**Effective Date:** 29 October 2026  
**Accountable QA Owner:** Anish (`planetai05`), QA Engineer  
**Related Backlog Issue:** [#32](https://github.com/Kundhan73/SE-MiniProject-SAMS/issues/32) (SAM-45)  
**Requirements Traced:** SAMS-NF-002 (Uptime & Availability), SAMS-NF-004 (Academic-Year Data Retention), SAMS-SR-005 (Append-Only Audit Trail)

---

## 1. Overview and Operational Scope

The Student Attendance Management System (SAMS) provides automated attendance marking, self-service student views, correction request workflows, notifications, and immutable audit logging. This Maintenance Plan defines procedures for backups, disaster recovery, software updates, operational monitoring, and team responsibilities to maintain system integrity and availability throughout the academic semester.

### Operational Targets
- **Target Availability:** >= 99% during working hours (8:00 AM – 6:00 PM, Monday through Saturday), excluding announced maintenance windows (SRS SAMS-NF-002).
- **Data Retention:** Retain all attendance, enrollment, and audit records for at least the full academic year without automatic purging (SRS SAMS-NF-004).
- **Audit Immutability:** Audit records are strictly append-only; database triggers and application code reject UPDATE and DELETE actions on audit logs (SRS SAMS-SR-005).

---

## 2. Backup Strategy

### 2.1 Backup Methodology and Tooling
- **Primary Database Engine:** PostgreSQL 16 (in Docker or hosted staging/production).
- **Tool:** Standard logical backup via `pg_dump` with gzip compression.
- **Backup Command:**
  ```bash
  docker compose exec -T db sh -c 'pg_dump -U "$POSTGRES_USER" --clean --if-exists --format=c "$POSTGRES_DB"' > /var/backups/sams/sams_backup_$(date +%Y%m%d_%H%M%S).dump
  ```
- **Scope:** Complete database schema, user accounts, timetables, course sections, attendance records, correction history, and append-only audit tables (`audit_auditlog`).

### 2.2 Schedule and Automation
- **Frequency:** Automated daily backups executed at 02:00 AM IST (off-peak hours) via system cron or container scheduler.
- **Pre-Migration Backups:** A mandatory ad-hoc backup must be created immediately prior to executing any Django database migration (`python manage.py migrate`).

### 2.3 Storage and Encryption
- **Location:** Backups are stored in an isolated, access-controlled directory outside the application directory. Under no circumstances are backup files committed to Git.
- **Encryption:** Backup dumps are encrypted at rest using AES-256 before transfer to secure offsite secondary storage.
- **Retention Schedule:**
  - Daily backups: Retained for 14 days.
  - Weekly snapshots (Sunday 02:00 IST): Retained for 8 weeks.
  - Monthly snapshots (1st of month): Retained for 12 months (1 full academic year) per SAMS-NF-004.

### 2.4 Integrity Verification
- **Automated Restore Testing:** Every Sunday at 04:00 AM IST, the latest backup is restored into an ephemeral test container. Automated sanity scripts verify:
  1. Successful database restoration without errors.
  2. Table row counts match source database.
  3. Append-only triggers are active on `audit_auditlog`.
  4. Migration status is cleanly reported by `python manage.py showmigrations`.

---

## 3. Disaster Recovery and Business Continuity

### 3.1 Objectives
- **Recovery Time Objective (RTO):** <= 2 hours for core attendance marking and viewing services.
- **Recovery Point Objective (RPO):** <= 24 hours (maximum data loss bounded by daily backup interval; intra-day classes can be re-entered from physical class rosters if catastrophic hardware failure occurs).

### 3.2 Step-by-Step Restoration Procedure
1. **Isolate and Stop Application:**
   ```bash
   docker compose stop web worker beat
   ```
2. **Verify Backup File Integrity:**
   ```bash
   # Verify archive checksum
   sha256sum -c /var/backups/sams/sams_backup_<timestamp>.dump.sha256
   ```
3. **Restore Database:**
   ```bash
   docker compose exec -T db pg_restore -U "$POSTGRES_USER" -d "$POSTGRES_DB" --clean --if-exists /var/backups/sams/sams_backup_<timestamp>.dump
   ```
4. **Validate Schema & Apply Pending Migrations:**
   ```bash
   docker compose run --rm web python manage.py migrate --check
   ```
5. **Restart Services & Smoke Test:**
   ```bash
   docker compose start web worker beat
   curl --fail http://localhost:8000/api/health/
   ```

### 3.3 Rehearsals
- Disaster recovery procedures must be rehearsed once per semester in a staging environment to validate runbooks and verify team readiness.

---

## 4. Updates, Patch Management, and Rollbacks

### 4.1 Dependency and Vulnerability Auditing
- **Automated Audits:** `pip-audit` runs on every GitHub Actions PR and push to `main`.
- **Review Cadence:** Weekly review of newly disclosed CVEs affecting Django, psycopg, ReportLab, Celery, or Redis.
- **Patch Policy:**
  - Critical/High CVEs: Patched within 48 hours.
  - Routine dependency updates: Bundled into scheduled sprint releases.

### 4.2 Maintenance Windows
- All routine updates and schema migrations must occur during announced maintenance windows: **Sundays 00:00 – 06:00 IST** or non-instructional holidays.
- Advance notice (minimum 24 hours) must be posted to faculty and administrative users.
- Announced maintenance windows are explicitly excluded when calculating semester uptime for SAMS-NF-002.

### 4.3 Container-Based Deployment and Rollback
- Application images are built deterministically and tagged with Git commit SHAs: `ghcr.io/kundhan73/se-miniproject-sams:sha-<commit>`.
- **Zero-Downtime Rollback:**
  If a newly deployed image exhibits unforeseen runtime defects, rollback to the previous known good commit tag is instantaneous:
  ```bash
  export IMAGE_TAG=sha-<previous-commit>
  docker compose up -d web worker beat
  ```
- If backward-incompatible database migrations were applied, the database must be restored from the pre-migration backup before pointing to the earlier container image.

---

## 5. Monitoring, Alerting, and Availability Tracking

### 5.1 Service Health Checks
- **Endpoint:** `GET /api/health/` (unauthenticated).
- **Probes:**
  - Database connectivity: Executes `SELECT 1` on PostgreSQL.
  - Cache/Broker connectivity: Issues `.ping()` to Redis when Celery is not in eager mode.
- **Responses:**
  - HTTP `200 OK`: `{"status": "ok"}`
  - HTTP `503 Service Unavailable`: `{"status": "unavailable"}` when Redis or DB is unreachable.

### 5.2 Working-Hours Uptime Monitoring (Issue #36 / SAMS-NF-002)
- **Schedule:** 8:00 AM – 6:00 PM IST, Monday through Saturday.
- **Probe Interval:** 60-second synthetic HTTP GET to `/api/health/`.
- **Target SLA:** 99.0% uptime over the semester.
- **Tracking Log:** Semester-long latency and status logs stored in monitoring service dashboard; monthly summary reports generated for compliance.

### 5.3 Asynchronous Task and Notification Alerting
- Failed email deliveries are captured in the database with retry counters, timestamps, and exact exception details (`email_error` and `email_attempts`).
- Administrators can monitor failures via `GET /api/admin/email-failures/`.
- Recurring low-attendance scans run nightly via Celery Beat (`nightly_scan` task).

---

## 6. Roles and Maintenance Responsibilities

| Role | Primary Member | Responsibilities |
| --- | --- | --- |
| **Developer** | Kundhan Vudutha (`Kundhan73`) | Implementation of patches, bug fixes, database migrations, Docker configuration, and CI/CD workflow updates. |
| **Tester** | Tarun J (`DarkTJ7`) | Independent execution of test suites after updates, verifying bug fixes (#45, #46), executing staging performance, ZAP, and accessibility tests. |
| **QA Engineer** | Anish (`planetai05`) | Monitoring compliance with SRS/SAD/STP, updating Requirements Traceability Matrix (`TRACEABILITY.md`), validating test and coverage reports, auditing maintenance records, and conducting PR release reviews. |
| **System Administrator (Ops)** | Faculty/IT Operations | Server OS patching, TLS certificate renewals, external DNS/Nginx configuration, offsite backup storage maintenance, and external uptime monitor administration. |

---

## 7. Compliance Verification Checklist

- [x] Automated database backup command verified and documented.
- [x] Recovery runbook tested against local Docker environment.
- [x] Rollback procedure documented using immutable container SHA tags.
- [x] `/api/health/` monitoring configured and tested for DB and Redis outages.
- [x] Maintenance window policy defined to preserve SAMS-NF-002 SLA boundaries.
- [x] Operational roles delineated across Developer, Tester, QA, and SysAdmin.
